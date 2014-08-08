from django.conf import settings

def get_javascript_catalog_packages(*packages):
    return packages + tuple(settings.DEVILRY_JAVASCRIPT_LOCALE_OVERRIDE_APPS)
