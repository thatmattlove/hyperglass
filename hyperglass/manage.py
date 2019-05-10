import os
import sys
import app
import logging

log = logging.getLogger(__name__)


def clearcache():
    try:
        app.clearCache()
    except:
        raise


for arg in sys.argv:
    if arg == "clearcache":
        try:
            clearcache()
        except:
            raise
