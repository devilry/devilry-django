from django.conf.urls.defaults import include

devilry_urls = ((r'^student/', include('devilry.apps.student.urls')),
                (r'^examiner/', include('devilry.apps.examiner.urls')),
                (r'^administrator/', include('devilry.apps.administrator.urls')),
                (r'^gradeeditors/', include('devilry.apps.gradeeditors.urls')),
                (r'^markup/', include('devilry.apps.markup.urls')),
                (r'^rest/1.0/admin/', include('devilry.apps.restadmin.urls')),
                (r'^authenticate/', include('devilry.apps.authenticate.urls')))
