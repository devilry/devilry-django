from django.conf.urls import patterns, url

urlpatterns = patterns('devilry.devilry_authenticate',
                       url(r'^logout$', 'views.logout', name='logout'),
                       url(r'^login$', 'views.login', name='login'))
