from collections import defaultdict
from functools import wraps

from api.websocket import sock_send
from utils.logs import L

# Dictionary to store event handlers, organized by event name and priority
event_registry = defaultdict(list)


# This decorator registers the decorated function as an event handler
def event_handler(event_name, priority=0):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # Register the handler by event name and priority
        event_registry[event_name].append((priority, wrapper))
        # Sort the handlers by priority (highest first)
        event_registry[event_name].sort(key=lambda x: -x[0])

        return wrapper

    return decorator


# This function triggers the event by calling all handlers associated with the event
def event_trigger(event_name, payload):
    if event_name in event_registry:
        for _, handler in event_registry[event_name]:
            handler(payload)
    else:
        L.warning(f"Unregistered event: {event_name}")


# Example usage
@event_handler("on_data", priority=1)
def handle_data_event(payload):
    print(f"Handling data event with payload: {payload}")


@event_handler("on_data", priority=2)
def another_data_handler(payload):
    print(f"Another handler for data event with payload: {payload}")


@event_handler("chat_to_persona")
def handle_chat_to_persona(payload):
    # event_trigger(
    #     "chat_to_persona", {"mode": mode, "persona": persona_name, "reply": retval}
    # )
    sock_send(
        "chat",
        {
            "sender": payload["persona"],
            "role": "agent",
            "type": "private",
            "content": payload["reply"],
            "timestamp": "",
            "subject": payload.get("subject", ""),
        },
    )


@event_handler("agent_comment")
def handle_chat(payload):
    """
    Send a chat message into frontend via websocket.

    Args:
        payload (dict): A dictionary containing the following keys:
            - "name" (str): The name of the agent sending the message.
            - "content" (str): The content of the chat message.

    Side-effects:
        Sends a formatted message via the `sock_send` function.

    Example:
        payload = {"name": "Agent Smith", "content": "Hello, how can I help you?"}
        handle_chat(payload)
        # This will send a message like:
        # {"role": "agent", "name": "Agent Smith", "content": "Hello, how can I help you?"}
    """
    sock_send(
        "chat",
        {
            "sender": payload["name"],
            "role": "agent",
            "type": "public",
            "content": payload["content"],
            "timestamp": "",
            "subject": payload.get("subject", ""),
        },
    )
