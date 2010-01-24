from django.conf.urls.defaults import *

urlpatterns = patterns('devilry.core',
	(r'^dashboard/$', 'views.dashboard'),
	(r'^deliver/$', 'views.deliver'),
)
