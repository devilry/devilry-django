from django.conf.urls.defaults import include
from django.contrib import admin

admin.autodiscover()


devilry_urls = ((r'^student/', include('devilry.apps.student.urls')),
                (r'^examiner/', include('devilry.apps.examiner.urls')),
                (r'^administrator/', include('devilry.apps.administrator.urls')),
                (r'^gradeeditors/', include('devilry.apps.gradeeditors.urls')),
                (r'^markup/', include('devilry.apps.markup.urls')),
                (r'^jsfiledownload/', include('devilry.apps.jsfiledownload.urls')),
                (r'^authenticate/', include('devilry.apps.authenticate.urls')),

                (r'^devilry_usersearch/', include('devilry_usersearch.urls')),
                (r'^superadmin/', include(admin.site.urls))
               )
