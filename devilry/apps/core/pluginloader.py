from django.apps import apps
from importlib import import_module

# A flag to tell us if autodiscover is running.  autodiscover will set this to
# True while running, and False when it finishes.
LOADING = False


def autodiscover():
    """
    Auto-discover INSTALLED_APPS devilry_plugin.py modules and fail silently when
    not present. This code is derived from the one used by the Django admin.
    """
    global LOADING
    if LOADING:
        return
    LOADING = True

    import imp
    from django.conf import settings

    for app in apps.get_app_configs():
        try:
            imp.find_module('devilry_plugin', app.module.__name__)
        except ImportError:
            continue

        import_module("%s.devilry_plugin" % app.module.__name)
    # autodiscover was successful, reset loading flag.
    LOADING = False
