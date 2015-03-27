from django.conf.urls import patterns, url
from django_cradmin.apps.cradmin_authenticate.views import login as cradmin_login

urlpatterns = patterns('devilry.devilry_authenticate',
                       url(r'^logout$', 'views.logout', name='logout'),
                       url(r'^login$', 'views.login', name='login'),
                       url(r'^email_login$', cradmin_login.LoginView.as_view(), name='cradmin-authenticate-login'))
