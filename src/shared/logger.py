"""logger configuration.

configure logging once at module import. all modules use standard python logging:

    import logging
    logger = logging.getLogger(__name__)
    
automatically includes file:line:function in logs.
"""

import logging
import sys

# configure root logger once
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] [%(name)s] [%(filename)s:%(lineno)d:%(funcName)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True,  # override any existing config
)
