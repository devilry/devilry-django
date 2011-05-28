from django.conf.urls.defaults import *
from django.conf import settings
from devilry.apps.core import pluginloader

from django.contrib import admin
admin.autodiscover()


debugpatterns = []
if settings.DEBUG:
    debugpatterns = [
        (r'^guiexamples/', include('devilry.apps.guiexamples.urls'))]

urlpatterns = patterns('',
    # Example:
    # (r'^devilry/', include('devilry.foo.urls')),

    (r'^accounts/login/$', 'django.contrib.auth.views.login'),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    #(r'^superadmin/doc/', include('django.contrib.admindocs.urls')),
    (r'^superadmin/', include(admin.site.urls)),

    (r'^restful/', include('devilry.apps.restful.urls')),
    (r'^ui/', include('devilry.apps.ui.urls')),
    (r'^student/', include('devilry.apps.student.urls')),
    (r'^examiner/', include('devilry.apps.examiner.urls')),
    (r'^admin/', include('devilry.apps.admin.urls')),
    (r'^grade_schema/', include('devilry.apps.grade_schema.urls')),
    (r'^grade_rstschema/', include('devilry.apps.grade_rstschema.urls')),
    (r'^gradestats/', include('devilry.apps.gradestats.urls')),
    (r'^adminscripts/', include('devilry.apps.adminscripts.urls')),
    (r'^xmlrpc/', include('devilry.apps.xmlrpc.urls')),
    (r'^xmlrpc_examiner/', include('devilry.apps.xmlrpc_examiner.urls')),
    (r'^', include('devilry.apps.quickdash.urls')),

    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.DEVILRY_STATIC_ROOT}),
    *debugpatterns
)


# Must be after url-loading to allow plugins to use reverse()
pluginloader.autodiscover()
