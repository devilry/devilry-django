from django.conf.urls.defaults import include
from django.contrib import admin
from devilry_frontpage.views import frontpage

admin.autodiscover()


devilry_urls = ((r'^student/', include('devilry.apps.student.urls')),
                (r'^examiner/', include('devilry.apps.examiner.urls')),
                (r'^administrator/', include('devilry.apps.administrator.urls')),
                (r'^gradeeditors/', include('devilry.apps.gradeeditors.urls')),
                (r'^markup/', include('devilry.apps.markup.urls')),
                (r'^jsfiledownload/', include('devilry.apps.jsfiledownload.urls')),
                (r'^authenticate/', include('devilry.apps.authenticate.urls')),

                (r'^devilry_usersearch/', include('devilry_usersearch.urls')),
                (r'^devilry_authenticateduserinfo/', include('devilry_authenticateduserinfo.urls')),
                (r'^devilry_settings/', include('devilry_settings.urls')),
                (r'^devilry_helplinks/', include('devilry_helplinks.urls')),
                (r'^devilry_student/', include('devilry_student.urls')),
                (r'^devilry_i18n/', include('devilry_i18n.urls')),
                (r'^superuser/', include(admin.site.urls)),
                (r'^devilry_frontpage/', include('devilry_frontpage.urls')),
                (r'^devilry_subjectadmin/', include('devilry_subjectadmin.urls')),
                (r'^devilry_send_email_to_students/', include('devilry.apps.send_email_to_students.urls')),
                (r'^devilry_search/', include('devilry_search.urls')),
                (r'^devilry_header/', include('devilry_header.urls')),
                ('^devilry_nodeadmin/', include('devilry_nodeadmin.urls')),
                (r'^devilry_qualifiesforexam/', include('devilry_qualifiesforexam.urls')),
                (r'^devilry_qualifiesforexam_approved/', include('devilry_qualifiesforexam_approved.urls')),
                (r'^devilry_qualifiesforexam_points/', include('devilry_qualifiesforexam_points.urls')),
                (r'^devilry_qualifiesforexam_select/', include('devilry_qualifiesforexam_select.urls')),
                (r'^$', frontpage),
               )
