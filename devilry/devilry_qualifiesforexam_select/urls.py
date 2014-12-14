from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from django.views.i18n import javascript_catalog
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie

from devilry.project.common.i18n import get_javascript_catalog_packages
from .views import QualifiesBasedOnManualSelectView
from .views import BuildExtjsAppView


i18n_packages = get_javascript_catalog_packages('devilry_extjsextras', 'devilry_header', 'devilry.apps.core', 'devilry_subjectadmin', 'devilry_qualifiesforexam', 'devilry_qualifiesforexam_select')




urlpatterns = patterns('devilry.devilry_qualifiesforexam_select',
    url('^$', login_required(csrf_protect(ensure_csrf_cookie(BuildExtjsAppView.as_view())))),
    url('^select$', login_required(csrf_protect(ensure_csrf_cookie(QualifiesBasedOnManualSelectView.as_view()))),
        name='devilry_qualifiesforexam_select'),
    url('^i18n.js$', javascript_catalog, kwargs={'packages': i18n_packages},
        name='devilry_qualifiesforexam_select_i18n')
)

