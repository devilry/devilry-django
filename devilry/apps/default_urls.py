from django.conf.urls.defaults import include, patterns

devilry_urlpatterns = patterns(#(r'^student/', include('devilry.apps.student.urls')),
                               #(r'^examiner/', include('devilry.apps.examiner.urls')),
                               (r'^administrator/', include('devilry.apps.administrator.urls')),
                               (r'^authenticate/', include('devilry.apps.authenticate.urls')))
