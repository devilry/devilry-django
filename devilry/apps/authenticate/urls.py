from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('devilry.apps.authenticate.views',
                       url(r'^logout$', 'logout', name='logout'),
                       url(r'^login$', 'login', name='login'))
