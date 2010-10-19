from django.conf.urls.defaults import *
from django.conf import settings
from devilry.core import pluginloader

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Example:
    # (r'^devilry/', include('devilry.foo.urls')),

    (r'^accounts/login/$', 'django.contrib.auth.views.login'),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    #(r'^superadmin/doc/', include('django.contrib.admindocs.urls')),

    (r'^superadmin/', include(admin.site.urls)),
    (r'^ui/', include('devilry.ui.urls')),
    (r'^student/', include('devilry.addons.student.urls')),
    (r'^examiner/', include('devilry.addons.examiner.urls')),
    (r'^admin/', include('devilry.addons.admin.urls')),
    (r'^grade_schema/', include('devilry.addons.grade_schema.urls')),
    (r'^grade_rstschema/', include('devilry.addons.grade_rstschema.urls')),
    (r'^gradestats/', include('devilry.addons.gradestats.urls')),
    (r'^adminscripts/', include('devilry.adminscripts.urls')),
    (r'^xmlrpc/', include('devilry.xmlrpc.urls')),
    (r'^xmlrpc_examiner/', include('devilry.addons.xmlrpc_examiner.urls')),
    (r'^', include('devilry.addons.quickdash.urls')),
    (r'^resources/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.DEVILRY_RESOURCES_ROOT}),
)


# Must be after url-loading to allow plugins to use reverse()
pluginloader.autodiscover()
