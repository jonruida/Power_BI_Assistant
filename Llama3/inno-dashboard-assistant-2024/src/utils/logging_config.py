#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Authors: SDG DS unit
"""
Module for configuring the logging system.

This module sets up the logging configuration for the application.
It ensures that the log directory exists and configures logging to 
both a log file and the console. The log file is stored in the 'logs'
directory, and the log level is set to DEBUG, allowing for detailed 
logs to be captured during the application's execution.
"""
import logging
import os

# Create the logs directory if it doesn't exist
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)


def setup_logging():
    """
    Sets up logging configuration for the application.

    This function configures the logging to output logs to both a log
    file and the console. The log file is stored in the 'logs' directory
    as 'app.log', and the log level is set to DEBUG. The log format includes
    the timestamp, logger name, log level, and message.

    The logging handlers are configured as follows:
        - FileHandler: Logs are saved to a file in the 'logs' directory.
        - StreamHandler: Logs are also printed to the console.
    """
    log_file = os.path.join(LOG_DIR, "app.log")
    logging.basicConfig(
        level=logging.DEBUG,  # Global log level
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(filename=log_file),  # Main log file
            logging.StreamHandler(),  # Log in the console
        ],
    )
