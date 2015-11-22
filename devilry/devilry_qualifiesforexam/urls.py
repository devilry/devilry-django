from django.conf.urls import patterns, url, include
from django.contrib.auth.decorators import login_required
from django.views.i18n import javascript_catalog
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie

from devilry.project.common.i18n import get_javascript_catalog_packages
from .views import AppView
from .views import StatusPrintView


i18n_packages = get_javascript_catalog_packages('devilry_extjsextras', 'devilry_header', 'devilry.apps.core', 'devilry_subjectadmin', 'devilry_qualifiesforexam')



urlpatterns = patterns('devilry.devilry_qualifiesforexam',
    url('^rest/', include('devilry.devilry_qualifiesforexam.rest.urls')),
    url('^$', login_required(csrf_protect(ensure_csrf_cookie(AppView.as_view()))),
        name='devilry_qualifiesforexam_ui'),
    url('^statusprint/(?P<status_id>\d+)$', login_required(StatusPrintView.as_view()),
        name='devilry_qualifiesforexam_statusprint'),
    url('^i18n.js$', javascript_catalog, kwargs={'packages': i18n_packages},
        name='devilry_qualifiesforexam_i18n')
)

