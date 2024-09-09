# consumers.py
import asyncio
import json
import logging
import time
from functools import wraps
from threading import Thread

from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer

from utils.logs import L

# Dictionary to store registered handlers
socket_handlers = {}


def socket_handler(sock_name):
    """
    Decorator to register a function as a handler for a specific socket name.
    """

    def decorator(func):
        socket_handlers[sock_name] = func

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


@database_sync_to_async
def handle_sock(sock_name, message, user):
    """
    Handle incoming socket messages by routing to the appropriate handler.
    """
    if sock_name in socket_handlers:
        return socket_handlers[sock_name](message, user)
    else:
        return f"No handler registered for {sock_name}"


class SocketConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Handle WebSocket connection.
        """
        sock_name = self.scope["url_route"]["kwargs"]["sock_name"]
        L.info(f"Websockets {sock_name} connecting...")
        self.sock_name = self.scope["url_route"]["kwargs"]["sock_name"]
        if self.sock_name not in socket_handlers:
            L.warning(f"No handler registered for {sock_name}")
            await self.close()
            return

        await self.channel_layer.group_add(self.sock_name, self.channel_name)
        await self.accept()
        L.info(f"Websockets {sock_name} connected.")

    async def disconnect(self, close_code):
        """
        Handle WebSocket disconnection.
        """
        if self.channel_layer:
            await self.channel_layer.group_discard(self.sock_name, self.channel_name)
        L.info(f"Websockets {self.sock_name} disconnected.")

    async def receive(self, text_data):
        """
        Handle incoming WebSocket messages.
        """
        response = await handle_sock(self.sock_name, text_data, self.scope["user"])
        await self.send(text_data=response)

    async def sock_message(self, event):
        """
        Handle messages sent to the WebSocket via the channel layer.
        """
        message = event["message"]
        await self.send(text_data=message)


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


def sock_send(sock_name, message):
    """
    Send a message to a specific socket group.
    """
    channel_layer = get_channel_layer()
    if not isinstance(message, str):
        message = json.dumps(message)
    async_to_sync(channel_layer.group_send)(sock_name, {"type": "sock_message", "message": message})


# Example usage of the socket_handler decorator
@socket_handler("default")
def default_handler(message, user):
    return f"Default handler: {message}"


# Example of an echo handler
@socket_handler("echo")
def echo_handler(message, user):
    return f"Echo: {message}"


# Example of a user info handler
@socket_handler("user_info")
def user_info_handler(message, user):
    return f"User {user.username} is connected. Message: {message}"


@socket_handler("log")
def log_socket_handler(message, user):
    # do nothing
    pass


@socket_handler("chat")
def chat_socket_handler(message, user):
    # do nothing
    pass


class WebSocketHandler(logging.Handler):
    def __init__(self, sock_name):
        super().__init__()
        self.sock_name = sock_name

    def emit(self, record):
        log_entry = self.format(record)
        try:
            sock_send(self.sock_name, log_entry)
        except Exception:
            # Do nothing if socket send is not successful
            pass


_socket_handler = WebSocketHandler("log")
L.add_handler(_socket_handler)
