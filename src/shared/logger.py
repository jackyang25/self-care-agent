"""logger configuration.

call setup_logging() once at application startup. all modules use standard python logging:

    import logging
    logger = logging.getLogger(__name__)
    
automatically includes file:line:function in logs.
"""

import logging
import sys


def setup_logging():
    """configure root logger for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] [%(name)s] [%(filename)s:%(lineno)d:%(funcName)s] %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,  # override any existing config
    )
