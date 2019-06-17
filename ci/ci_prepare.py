#!/usr/bin/env python3

import os
import glob
import shutil
from logzero import logger


def ci_copy_config():
    """Copies test configuration files to usable config files"""
    logger.info("Migrating test config files...")
    config_dir = os.path.join(parent_directory, "hyperglass/configuration/")
    test_files = glob.iglob(os.path.join(working_directory, "*.toml"))
    config_files = glob.iglob(os.path.join(config_dir, "*.toml"))
    logger.debug(config_dir)
    logger.debug(working_directory)
    logger.debug(parent_directory)
    status = False
    for f in config_files:
        if os.path.exists(f):
            logger.debug(f"{f} already exists")
            os.remove(f)
            logger.debug(f"Deleted {f}")
    for f in test_files:
        try:
            shutil.copy(f, config_dir)
            logger.debug(f"Copied {f}")
            logger.info("Successfully migrated test config files")
            status = True
        except:
            logger.error(f"Failed to migrate {f}")
            raise
    return status


if __name__ == "__main__":
    ci_copy_config()
