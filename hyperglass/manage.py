import os
import sys
import app


def clearcache():
    try:
        app.clearCache()
    except:
        raise


for arg in sys.argv:
    try:
        if arg == "clearcache":
            clearcache()
            print("Successfully cleared cache.")
    except:
        print("Failed to clear cache.")
        raise
