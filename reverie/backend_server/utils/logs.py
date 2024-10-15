import inspect
import io
import logging
import os

import colorlog
from tabulate import tabulate


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
_logger.setLevel(get_log_level())
_logger.propagate = False

_term_logger = colorlog.getLogger("NATIVE")
_term_logger.addHandler(_color_handler)
_term_logger.setLevel(get_log_level())
_term_logger.propagate = False


def get_outer_caller():
    """
    Returns the name of the nearest caller function that is outside the module
    that called get_outer_caller().

    If no such caller is found, returns None.
    """
    # Get the current frame (inside get_outer_caller)
    current_frame = inspect.currentframe()
    try:
        # The caller of get_outer_caller is one frame back
        caller_frame = current_frame.f_back
        if not caller_frame:
            return None

        # Determine the module of the caller
        caller_module = inspect.getmodule(caller_frame)
        caller_module_name = caller_module.__name__ if caller_module else None

        # Start traversing the call stack from the caller's frame
        frame = caller_frame.f_back
        while frame:
            # Get the module of the current frame
            module = inspect.getmodule(frame)
            module_name = module.__name__ if module else None

            # If the module is different from the caller's module, we've found the external caller
            if module_name != caller_module_name:
                func_name = frame.f_code.co_name
                # Optionally, skip '<module>' if you only want function names
                if func_name != "<module>":
                    return func_name
                else:
                    # If the caller is at the module level, return None or a placeholder
                    return None  # or '<module>'

            # Move to the previous frame in the stack
            frame = frame.f_back

        # If no external caller is found
        return None
    finally:
        # Explicitly delete frame references to avoid reference cycles
        del current_frame
        del caller_frame
        del frame


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
    def info(msg, *args, enabled=False, native=False, **kwargs):
        if enabled or is_default_enabled():
            if native:
                _term_logger.info(msg, *args, **kwargs)
            else:
                _logger.info(msg, *args, **kwargs)

    @staticmethod
    def warning(msg, *args, enabled=False, native=False, **kwargs):
        if enabled or is_default_enabled():
            if native:
                _term_logger.warning(msg, *args, **kwargs)
            else:
                _logger.warning(msg, *args, **kwargs)

    @staticmethod
    def debug(msg, *args, enabled=False, native=False, **kwargs):
        if enabled or is_default_enabled():
            if native:
                _term_logger.debug(msg, *args, **kwargs)
            else:
                _logger.debug(msg, *args, **kwargs)

    @staticmethod
    def error(msg, *args, enabled=False, native=False, **kwargs):
        if enabled or is_default_enabled():
            if native:
                _term_logger.error(msg, *args, **kwargs)
            else:
                _logger.error(msg, *args, **kwargs)

    @staticmethod
    def critical(msg, *args, enabled=False, native=False, **kwargs):
        if enabled or is_default_enabled():
            if native:
                _term_logger.critical(msg, *args, **kwargs)
            else:
                _logger.critical(msg, *args, **kwargs)

    @staticmethod
    def exception(msg, *args, enabled=False, native=False, **kwargs):
        if enabled or is_default_enabled():
            if native:
                _term_logger.exception(msg, *args, **kwargs)
            else:
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
    def print_stats(native=False):
        logger = _logger if not native else _term_logger

        # Prepare Overall Stats
        overall_headers = ["Metric", "Value"]
        overall_data = [
            ["Total Requests", _all_stats.total_requests],
            ["Total Duration (s)", f"{_all_stats.total_duration:.2f}"],
            ["Prompt Tokens", _all_stats.prompt_tokens],
            ["Completion Tokens", _all_stats.completion_tokens],
            ["Successful Requests", _all_stats.success_requests],
        ]

        overall_table = tabulate(overall_data, headers=overall_headers, tablefmt="grid")
        logger.info("=== Overall Usage Stats ===")
        logger.info("\n%s", overall_table)

        # Prepare Function-Specific Stats
        if _stats_by_func:
            func_headers = [
                "Function Name",
                "Total Requests",
                "Total Duration (s)",
                "Prompt Tokens",
                "Completion Tokens",
                "Successful Requests",
            ]
            func_data = []
            for function_name, fstat in _stats_by_func.items():
                func_data.append(
                    [
                        function_name,
                        fstat.total_requests,
                        f"{fstat.total_duration:.2f}",
                        fstat.prompt_tokens,
                        fstat.completion_tokens,
                        fstat.success_requests,
                    ]
                )

            func_table = tabulate(func_data, headers=func_headers, tablefmt="grid")
            logger.info("\n=== Usage Stats by Function ===")
            logger.info("\n%s", func_table)
        else:
            logger.info("\n=== Usage Stats by Function ===")
            logger.info("No function-specific stats available.")

    @staticmethod
    def set_level(level):
        _term_logger.setLevel(level)
        _logger.setLevel(level)

    @staticmethod
    def add_handler(handler):
        _logger.addHandler(handler)
