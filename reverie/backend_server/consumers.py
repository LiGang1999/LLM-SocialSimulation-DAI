# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio
import io
from log import L, log_stream

import subprocess
from reverie import online_relation
from threading import Thread
import time


class LogConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = "console_log"
        L.info("Websockets connecting...")
        await self.accept()

        L.info("Websockets connected")

        try:
            last_position = 0  # Initialize to track the last read position in the log_stream

            while True:
                # Get the current position in the stream and check if there's new content
                current_position = log_stream.tell()

                if current_position > last_position:
                    log_stream.seek(last_position)
                    new_content = log_stream.read()
                    last_position = log_stream.tell()

                    # Send the new content to the WebSocket client
                    await self.send(text_data=new_content)

                await asyncio.sleep(0.5)  # Small sleep to prevent a tight loop

        except asyncio.CancelledError:
            L.info("Websockets disconnected due to cancelled task.")
        except Exception as e:
            L.error(f"Error in Websockets log streaming: {e}")

    async def disconnect(self, close_code):
        L.info(f"Websockets disconnected with code: {close_code}")


class OnlineConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.thread = Thread(target=self.get_online)
        self.thread.daemon = True
        self.thread.start()

    async def connect(self):
        print("online connecting..")
        await self.accept()
        print("online connected")

    def get_online(self):
        print("online - watch log and send")
        while True:
            if not online_relation.empty():
                line = online_relation.get()
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(
                        self.send(text_data=json.dumps({"message": line}))
                    )
                except Exception as e:
                    print("error: ", e)
            time.sleep(1)

    async def disconnect(self, close_code):
        pass
