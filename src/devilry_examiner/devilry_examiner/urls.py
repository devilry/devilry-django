from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.views.i18n import javascript_catalog

from devilry_settings.i18n import get_javascript_catalog_packages
from .views.dashboard import DashboardView
from .views.singlegroupoverview import SingleGroupOverview


i18n_packages = get_javascript_catalog_packages(
    #'devilry_examiner',
    'devilry_extjsextras', 'devilry.apps.core')

urlpatterns = patterns('devilry_examiner',
                       url('^rest/', include('devilry_examiner.rest.urls')),
                       url('^$', login_required(DashboardView.as_view()),
                           name='devilry_examiner_dashboard'),
                       url('^singlegroupoverview/(?P<groupid>\d+)$', login_required(SingleGroupOverview.as_view()),
                           name='devilry_examiner_singlegroupoverview'),
                       url('^i18n.js$', javascript_catalog, kwargs={'packages': i18n_packages},
                           name='devilry_examiner_i18n')
                       )

