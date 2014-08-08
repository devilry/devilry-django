"""
Utility functions for management commands.
"""

import logging


def setup_logging(verbosity):
    if verbosity < 1:
        loglevel = logging.ERROR
    elif verbosity == 1:
        loglevel = logging.WARNING
    elif verbosity == 2:
        loglevel = logging.INFO
    else:
        loglevel = logging.DEBUG
    logging.basicConfig(level=loglevel)


def get_verbosity(options):
    return int(options.get('verbosity', '1'))
