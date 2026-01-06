"""logger configuration for docker-friendly logging."""

import logging
import sys
from typing import Any, Union

from src.shared.context import current_user_id, channel, correlation_id


_loggers: dict[str, logging.Logger] = {}


class ContextLoggerAdapter(logging.LoggerAdapter):
    """logger adapter that automatically includes context variables."""

    def process(self, msg, kwargs):
        """add context variables to log messages."""

        # build context string
        context_parts = []

        user_id = current_user_id.get()
        if user_id:
            # truncate long user_id for readability
            context_parts.append(f"user:{user_id[:8]}")

        chan = channel.get()
        if chan:
            context_parts.append(f"channel:{chan}")

        corr_id = correlation_id.get()
        if corr_id:
            # truncate correlation_id for readability
            context_parts.append(f"corr:{corr_id[:8]}")

        # prepend context to message if any context exists
        if context_parts:
            context_str = " ".join(f"[{part}]" for part in context_parts)
            msg = f"{context_str} {msg}"

        return msg, kwargs


def get_logger(name: str = "app") -> Union[logging.Logger, ContextLoggerAdapter]:
    """get or create logger instance with context adapter."""
    if name in _loggers:
        base_logger = _loggers[name]
    else:
        base_logger = logging.getLogger(name)
        base_logger.setLevel(logging.INFO)

        # prevent duplicate handlers
        if not base_logger.handlers:
            # create console handler with docker-friendly format
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(logging.INFO)

            # format: timestamp, level, name, message
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            handler.setFormatter(formatter)

            base_logger.addHandler(handler)

        _loggers[name] = base_logger

    # wrap logger with context adapter
    return ContextLoggerAdapter(base_logger, {})


def get_tool_logger(tool_name: str) -> Union[logging.Logger, ContextLoggerAdapter]:
    """get logger instance for a tool.

    args:
        tool_name: name of the tool (e.g., "triage", "pharmacy")

    returns:
        logger instance configured for the tool
    """
    return get_logger(tool_name)


def log_tool_call(logger: Union[logging.Logger, ContextLoggerAdapter], tool_name: str, **kwargs: Any) -> None:
    """log tool call with arguments.

    args:
        logger: logger instance
        tool_name: name of the tool being called
        **kwargs: tool arguments to log
    """
    if kwargs:
        # format arguments for logging
        args_dict = {k: v for k, v in kwargs.items() if v is not None}
        logger.info(f"calling tool: {tool_name} with args: {args_dict}")
    else:
        logger.info(f"{tool_name} called")
