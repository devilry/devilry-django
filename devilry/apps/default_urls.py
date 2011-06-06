from django.conf.urls.defaults import include
from django.conf import settings

devilry_urls = [
    #(r'^restful/', include('devilry.apps.restful.urls')),
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
]

fileserve_url = (r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.DEVILRY_STATIC_ROOT})
