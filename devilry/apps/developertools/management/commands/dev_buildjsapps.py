import logging
from os.path import join, exists, dirname, isdir
from os import makedirs

from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.importlib import import_module
from devilry.apps import extjshelpers

from devilry.utils.command import setup_logging, get_verbosity


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

def get_js_apps():
    apps = []
    for moddir, mod, appname in get_installed_apps():
        staticdir = join(moddir, 'static')
        appfile = join(staticdir, 'app.js')
        if exists(appfile):
            apps.append((staticdir, appname))
    return apps


class Command(BaseCommand):
    help = 'Build JS apps.'

    def handle(self, *args, **options):
        setup_logging(get_verbosity(options))
        for appinfo in get_js_apps():
            self._buildApp(*appinfo)

    def _buildApp(self, staticdir, appname):
       pass 
