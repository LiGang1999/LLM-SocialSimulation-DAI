import logging
import colorlog
import os
import io


def get_log_level(default="DEBUG"):
    level = os.getenv("LOG_LEVEL", default).upper()
    return getattr(logging, level, logging.INFO)


def is_default_enabled():
    """
    By default, logging is enabled for the whole project.However, sometimes we want that only specified debug logs are printed.
    This can be achieved by setting LOG_ENABLED environment variable to false, and passing enabled=True to the log function we want to enable.
    """
    return os.getenv("LOG_ENABLED", "true").lower() == "true"


# Create a handler
_color_handler = colorlog.StreamHandler()
log_stream = io.StringIO()
_stream_handler = logging.StreamHandler(log_stream)

# Define a formatter with colors for different log levels
_formatter = colorlog.ColoredFormatter(
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
_color_handler.setFormatter(_formatter)

_root_logger = logging.getLogger()
if _root_logger.hasHandlers():
    _root_logger.handlers.clear()

# Create a logger instance and set its level
_logger = colorlog.getLogger("GLOBAL")
_logger.addHandler(_color_handler)
_logger.addHandler(_stream_handler)
_logger.setLevel(get_log_level())
_logger.propagate = False


class L:
    @staticmethod
    def info(msg, *args, enabled=False, **kwargs):
        if enabled or is_default_enabled():
            _logger.info(msg, *args, **kwargs)

    @staticmethod
    def warning(msg, *args, enabled=False, **kwargs):
        if enabled or is_default_enabled():
            _logger.warning(msg, *args, **kwargs)

    @staticmethod
    def debug(msg, *args, enabled=False, **kwargs):
        if enabled or is_default_enabled():
            _logger.debug(msg, *args, **kwargs)

    @staticmethod
    def error(msg, *args, enabled=False, **kwargs):
        if enabled or is_default_enabled():
            _logger.error(msg, *args, **kwargs)

    @staticmethod
    def critical(msg, *args, enabled=False, **kwargs):
        if enabled or is_default_enabled():
            _logger.critical(msg, *args, **kwargs)

    @staticmethod
    def exception(msg, *args, enabled=False, **kwargs):
        if enabled or is_default_enabled():
            _logger.exception(msg, *args, **kwargs)

    @staticmethod
    def set_level(level):
        _logger.setLevel(level)
