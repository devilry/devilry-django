from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('devilry.apps.authenticate',
                       url(r'^logout$', 'views.logout', name='logout'),
                       url(r'^login$', 'views.login', name='login'))
