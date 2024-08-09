import logging
import colorlog
import os


def get_log_level(default="DEBUG"):
    level = os.getenv("LOG_LEVEL", default).upper()
    return getattr(logging, level, logging.INFO)


# Create a handler
handler = colorlog.StreamHandler()

# Define a formatter with colors for different log levels
formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    log_colors={
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold_red",
    },
)

# Set the formatter for the handler
handler.setFormatter(formatter)

root_logger = logging.getLogger()
if root_logger.hasHandlers():
    root_logger.handlers.clear()

# Create a logger instance and set its level
L = colorlog.getLogger("GLOBAL")
L.addHandler(handler)
L.setLevel(get_log_level())
L.propagate = False
