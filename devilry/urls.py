from django.conf.urls.defaults import *
from django.conf import settings
from devilry.core import pluginloader

from django.contrib import admin
admin.autodiscover()

print "pluginloader.autodiscover"

pluginloader.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^devilry/', include('devilry.foo.urls')),

    (r'^accounts/login/$', 'django.contrib.auth.views.login'),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    (r'^admin/', include(admin.site.urls)),
    (r'^ui/', include('devilry.ui.urls')),
    (r'^studentview/', include('devilry.addons.studentview.urls')),
    (r'^examinerview/', include('devilry.addons.examinerview.urls')),
    (r'^adminview/', include('devilry.addons.adminview.urls')),
    (r'^dashboard/', include('devilry.addons.dashboard.urls')),
    (r'^', include('devilry.addons.dashboard.urls')),
    (r'^resources/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.DEVILRY_RESOURCES_ROOT}),
)
