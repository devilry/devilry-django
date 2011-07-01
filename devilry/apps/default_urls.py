from django.conf.urls.defaults import include
from django.conf import settings

devilry_urls = [#(r'^student/', include('devilry.apps.student.urls')),
                #(r'^examiner/', include('devilry.apps.examiner.urls')),
                (r'^administrator/', include('devilry.apps.administrator.urls')),
                (r'^authenticate/', include('devilry.apps.authenticate.urls'))]

fileserve_url = (r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.DEVILRY_STATIC_ROOT})
