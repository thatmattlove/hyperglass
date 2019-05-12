import os
import sys
from loguru import logger

# from hyperglass.hyperglass import app

logger.add(sys.stderr)


for arg in sys.argv:
    if arg == "clearcache":
        try:
            hyperglass.hyperglass.app.clearcache()
            logger.info("Successfully cleared cache.")
        except:
            raise
            logger.error("Failed to clear cache.")
