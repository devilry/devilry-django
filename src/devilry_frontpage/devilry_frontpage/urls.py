from django.conf.urls import patterns, url
from django.views.i18n import javascript_catalog

from devilry_settings.i18n import get_javascript_catalog_packages
from .views import old_frontpage


i18n_packages = get_javascript_catalog_packages('devilry_frontpage', 'devilry_header', 'devilry.apps.core')

urlpatterns = patterns('devilry_frontpage',
    url('^old$', old_frontpage, name='devilry_frontpage_old'),
    url('^i18n.js$', javascript_catalog, kwargs={'packages': i18n_packages},
        name='devilry_frontpage_i18n'))
