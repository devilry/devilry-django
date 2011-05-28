from django.conf.urls.defaults import *

urlpatterns = patterns('devilry.addons.grade_schema',
    (r'^edit-schema/(?P<assignment_id>\d+)$', 'views.edit_schema'),
    (r'^successful-save/(?P<assignment_id>\d+)$', 'views.successful_save'),
)
