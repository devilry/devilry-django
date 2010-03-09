from django.conf.urls.defaults import *
from django.conf import settings
from devilry.core import pluginloader

from django.contrib import admin
admin.autodiscover()

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
    (r'^studentview/', include('devilry.studentview.urls')),
    (r'^examinerview/', include('devilry.examinerview.urls')),
    (r'^adminview/', include('devilry.adminview.urls')),

    (r'^resources/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.DEVILRY_RESOURCES_ROOT}),
)
