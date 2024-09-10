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

from utils import thread_local
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


def sock_send(message, message_type):
    """
    Send a message to a specific socket group.
    """
    # sock_name is deprecated.
    if hasattr(thread_local, "reverie_instance"):
        reverie_instance = thread_local.reverie_instance
        message = json.dumps({"type": message_type, "message": message})
        reverie_instance.reverie.message_queue.put(message)


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
            sock_send({"level": record.levelname, "message": log_entry}, "log")
        except Exception as e:
            # Do nothing if socket send is not successfu
            L.warning(f"Failed to send log message to socket: {e}", native=True)
            pass


_socket_handler = WebSocketHandler("log")
L.add_handler(_socket_handler)
