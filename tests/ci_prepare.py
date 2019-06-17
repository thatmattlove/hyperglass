#!/usr/bin/env python3
"""
Prepares the test environment prior to starting hyperglass.
"""
import os
import glob
import shutil
from logzero import logger

working_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(working_directory)


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
    for file in config_files:
        if os.path.exists(file):
            logger.debug(f"{file} already exists")
            os.remove(file)
            logger.info(f"Deleted {file}")
    for file in test_files:
        try:
            shutil.copy(file, config_dir)
            logger.debug(f"Copied {file}")
            logger.debug(os.listdir(config_dir))
            logger.info("Successfully migrated test config files")
            status = True
        except:
            logger.error(f"Failed to migrate {file}")
            raise
    return status


if __name__ == "__main__":
    ci_copy_config()
