from os.path import exists, dirname, isdir, join

from django.conf import settings
from django.utils.importlib import import_module



def get_installed_apps():
    """
    Get all installed apps except for those in the ``django`` package.

    :return: List of installed apps as a list of ``(appdir, module, appname)``.
    """
    installed_apps = []
    checked = set()
    for app in settings.INSTALLED_APPS:
        if not app.startswith('django.') and not app in checked:
            mod = import_module(app)
            checked.add(app)
            if exists(mod.__file__) and isdir(dirname(mod.__file__)):
                appdir = dirname(mod.__file__)
                installed_apps.append((appdir, mod, mod.__name__.split('.')[-1]))
    return installed_apps


def get_staticdir(appdir, appname):
    return join(appdir, 'static', appname)

def get_staticdir_from_appname(appname, installed_apps=None):
    """
    Search installed apps for ``appname``, and if it is found, return its
    ``static/<appname>`` directory path.

    :param installed_apps: Defaults to getting this value from :func:`get_installed_apps`.
    :raise ValueError: If ``appname`` is not in ``installed_apps``.
    """
    if not installed_apps:
        installed_apps = get_installed_apps()
    for appdir, mod, name in installed_apps:
        if name == appname:
            return get_staticdir(appdir, appname)
    raise ValueError('{0} is not in installed_apps.'.format(appname))
