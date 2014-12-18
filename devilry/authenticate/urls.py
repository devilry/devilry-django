from django.conf.urls import patterns, url

urlpatterns = patterns('devilry.authenticate',
                       url(r'^logout$', 'views.logout', name='logout'),
                       url(r'^login$', 'views.login', name='login'))
