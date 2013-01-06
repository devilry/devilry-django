from django.conf.urls import patterns, url, include
from django.contrib.auth.decorators import login_required
from django.views.i18n import javascript_catalog
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie


from devilry_settings.i18n import get_javascript_catalog_packages
from .views import AppView


i18n_packages = get_javascript_catalog_packages('devilry_header', 'devilry.apps.core')



urlpatterns = patterns('devilry_qualifiesforexam',
    url('^rest/', include('devilry_qualifiesforexam.rest.urls')),
    url('^$', login_required(csrf_protect(ensure_csrf_cookie(AppView.as_view()))),
        name='devilry_qualifiesforexam_ui'),
    url('^i18n.js$', javascript_catalog, kwargs={'packages': i18n_packages},
        name='devilry_qualifiesforexam_i18n')
)

