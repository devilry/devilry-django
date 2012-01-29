"""
Utility functions for management commands.
"""

import logging
from os.path import exists, dirname, isdir

from django.conf import settings
from django.utils.importlib import import_module


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


def get_installed_apps():
    installed_apps = []
    checked = set()
    for app in settings.INSTALLED_APPS:
        if not app.startswith('django.') and not app in checked:
            mod = import_module(app)
            checked.add(app)
            if exists(mod.__file__) and isdir(dirname(mod.__file__)):
                moddir = dirname(mod.__file__)
                installed_apps.append((moddir, mod, mod.__name__.split('.')[-1]))
    return installed_apps
