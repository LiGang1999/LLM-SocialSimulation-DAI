import asyncio
import threading
import time
from collections import OrderedDict
from datetime import datetime

from jwt.exceptions import PyJWTError

from backend_server.reverie import Reverie, ReverieConfig


class ReverieInstance:
    def __init__(self, username, template_config, sim_config: ReverieConfig):
        self.initialized = False
        self.last_accessed = datetime.now()
        self.active_websockets = {}
        self.ws_lock = threading.Lock()
        self.reverie = Reverie(username, template_config, sim_config=sim_config)
        self.template_sim_code = template_config["template_sim_code"]
        self.sim_config = sim_config
        # more code for ReverieInstance is omitted

        self.message_sender_thread = threading.Thread(target=self.message_sender_loop, daemon=True)
        self.message_sender_thread.start()

    async def send_message_to_websockets(self, message):
        with self.ws_lock:
            if not self.active_websockets:
                return False

            disconnected_sockets = []
            for ws_id, websocket in self.active_websockets.items():
                try:
                    await websocket.send_text(message)
                except PyJWTError:
                    disconnected_sockets.append(ws_id)
                except Exception:
                    disconnected_sockets.append(ws_id)

            # Remove disconnected WebSockets
            for ws_id in disconnected_sockets:
                self.active_websockets.pop(ws_id, None)

            return bool(self.active_websockets)

    def message_sender_loop(self):
        while True:
            if not self.reverie.message_queue.empty() and self.active_websockets:
                message = self.reverie.message_queue.get()
                success = asyncio.run(self.send_message_to_websockets(message))
                if not success:
                    # If no active WebSockets, put the message back in the queue
                    self.reverie.message_queue.put(message)
            else:
                # Sleep briefly to avoid busy-waiting
                time.sleep(0.1)

    def shutdown(self):
        with self.ws_lock:
            self.message_sender_thread.join(timeout=5)  # Wait for the thread to finish
            # Close all active WebSockets
            for websocket in self.active_websockets.values():
                asyncio.run(websocket.close())
            self.active_websockets.clear()


class ReveriePool:
    def __init__(self, max_instances: int = 1000):
        self.max_instances = max_instances
        self.pool: OrderedDict[str, OrderedDict[str, ReverieInstance]] = OrderedDict()
        self.lock = threading.Lock()

    def get_or_create(
        self, sim_code: str, username: str, template_config: dict, sim_config: ReverieConfig
    ) -> ReverieInstance:
        with self.lock:
            if username not in self.pool:
                self.pool[username] = OrderedDict()

            if sim_code in self.pool[username]:
                # Move accessed item to the end (most recently used)
                reverie = self.pool[username].pop(sim_code)
                self.pool[username][sim_code] = reverie
            else:
                # Check total instance count before creating a new one
                total_instances = sum(len(user_pool) for user_pool in self.pool.values())
                if total_instances >= self.max_instances:
                    # Find and remove the oldest instance across all users
                    oldest_user = None
                    oldest_sim_code = None
                    oldest_time = datetime.now()

                    for user, user_pool in self.pool.items():
                        if user_pool:
                            # The first item in OrderedDict is the oldest
                            first_sim_code, first_reverie = next(iter(user_pool.items()))
                            if first_reverie.last_accessed < oldest_time:
                                oldest_time = first_reverie.last_accessed
                                oldest_user = user
                                oldest_sim_code = first_sim_code

                    if oldest_user and oldest_sim_code:
                        oldest_reverie = self.pool[oldest_user].pop(oldest_sim_code)
                        oldest_reverie.shutdown()
                        if not self.pool[oldest_user]:
                            self.pool.pop(oldest_user)  # Remove user if no more instances

                reverie = ReverieInstance(username, template_config, sim_config)
                self.pool[username][sim_code] = reverie
            return reverie

    def remove(self, username: str, sim_code: str) -> None:
        with self.lock:
            if username in self.pool and sim_code in self.pool[username]:
                reverie = self.pool[username].pop(sim_code)
                reverie.shutdown()  # Shutdown the removed instance
                if not self.pool[username]:
                    self.pool.pop(username)  # Remove user if no more instances

    def get(self, username: str, sim_code: str) -> ReverieInstance | None:
        with self.lock:
            if username in self.pool and sim_code in self.pool[username]:
                # Move accessed item to the end (most recently used)
                reverie = self.pool[username].pop(sim_code)
                self.pool[username][sim_code] = reverie
                return reverie
            return None

    def __len__(self) -> int:
        with self.lock:
            return sum(len(user_pool) for user_pool in self.pool.values())
