from django.conf.urls import patterns, url
from django_cradmin.apps.cradmin_authenticate.views.login import LoginView


urlpatterns = patterns(
    'django_cradmin.apps.cradmin_authenticate.views',
    url(r'^login$', LoginView.as_view(), name='cradmin-authenticate-login'),
    url(r'^logout$', 'logout.cradmin_logoutview', name='cradmin-authenticate-logout'),
)
