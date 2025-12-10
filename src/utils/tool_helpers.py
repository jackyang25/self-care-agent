"""common utilities for tool implementations."""

import json
import logging
from typing import Any, Dict
from src.utils.logger import get_logger


def get_tool_logger(tool_name: str) -> logging.Logger:
    """get logger instance for a tool.
    
    args:
        tool_name: name of the tool (e.g., "triage", "pharmacy")
    
    returns:
        logger instance configured for the tool
    """
    return get_logger(tool_name)


def log_tool_call(logger: logging.Logger, tool_name: str, **kwargs: Any) -> None:
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


def format_tool_response(
    status: str = "success",
    **data: Any
) -> str:
    """format tool response as structured JSON.
    
    args:
        status: response status (default: "success")
        **data: additional fields to include in response
    
    returns:
        json string with formatted response
    """
    result = {"status": status, **data}
    return json.dumps(result, indent=2)


def create_tool_response(
    status: str = "success",
    **data: Any
) -> Dict[str, Any]:
    """create tool response dictionary (before JSON serialization).
    
    args:
        status: response status (default: "success")
        **data: additional fields to include in response
    
    returns:
        dictionary with response data
    """
    return {"status": status, **data}

