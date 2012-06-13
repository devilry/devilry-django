from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.views.i18n import javascript_catalog
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie

from views import AppView

i18n_packages = ('devilry_subjectadmin', 'devilry_extjsextras')

urlpatterns = patterns('devilry_subjectadmin',
                       url('^rest/', include('devilry_subjectadmin.rest.urls')),
                       url('^$', login_required(csrf_protect(ensure_csrf_cookie(AppView.as_view())))),
                       url('^i18n.js$', javascript_catalog, kwargs={'packages': i18n_packages},
                           name='devilry_subjectadmin_i18n'))
