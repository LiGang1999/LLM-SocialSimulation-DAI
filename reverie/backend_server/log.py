import logging
import colorlog
import os
import inspect
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


def get_outer_caller(module_name) -> str:
    # Iterate over the call stack
    ret = ""
    for frame_info in inspect.stack():
        # Get the module of the current frame
        frame = frame_info.frame
        module = inspect.getmodule(frame)

        # Check if the module name matches the one we're looking for
        # if module and module.__name__ != module_name:
        modstr = f"{module.__name__}"
        if __name__ not in modstr and module_name not in modstr:
            ret = f"{modstr}.{frame_info.function}"
            return ret

    return ret  # Return None if no outer caller is found


class _UsageStats:
    total_requests: int = 0
    success_requests: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_duration: float = 0.0

    def __init__(self):
        self.completion_tokens = 0
        self.prompt_tokens = 0
        self.total_duration = 0.0
        self.total_requests = 0
        self.success_requests = 0


_all_stats = _UsageStats()
_stats_by_func = dict()


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
    def stats(function_name, model, is_chat, duration, request_tokens, response_tokens, valid):
        fstat = _stats_by_func.get(function_name, _UsageStats())
        fstat.total_requests += 1
        fstat.total_duration += duration
        fstat.prompt_tokens += request_tokens
        fstat.completion_tokens += response_tokens
        if valid:
            fstat.success_requests += 1
        _stats_by_func[function_name] = fstat

        _all_stats.total_requests += 1
        _all_stats.total_duration += duration
        _all_stats.prompt_tokens += request_tokens
        _all_stats.completion_tokens += response_tokens
        if valid:
            _all_stats.success_requests += 1

    @staticmethod
    def print_stats():
        _logger.info("Usage stats:")
        _logger.info("Total requests: %d", _all_stats.total_requests)
        _logger.info("Total duration: %f", _all_stats.total_duration)
        _logger.info("Prompt tokens: %d", _all_stats.prompt_tokens)
        _logger.info("Completion tokens: %d", _all_stats.completion_tokens)

    @staticmethod
    def set_level(level):
        _logger.setLevel(level)
