from django.conf.urls.defaults import *
from core import userview

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^devilry/', include('devilry.foo.urls')),

    (r'^accounts/login/$', 'django.contrib.auth.views.login'),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    (r'^admin/', include(admin.site.urls)),
    (r'^userview/', include(userview.site.urls)),

    (r'^core/', include('devilry.core.urls')),
)
