from django.conf.urls.defaults import *

urlpatterns = patterns('devilry.addons.student',
    url(r'^$', 'views.show_assignments', name='devilry-student-show-assignments'),
    url(r'^(?P<assignmentgroup_id>\d+)$', 'views.show_assignmentgroup', name='devilry-student-show-assignmentgroup'),
    url(r'^delivery/(?P<delivery_id>\d+)$', 'views.show_delivery', name='devilry-student-show-delivery'),
    url(r'^add-delivery/(?P<assignment_group_id>\d+)$', 'views.add_delivery', name='devilry-student-add-delivery'),
    url(r'^successful-delivery/(?P<assignment_group_id>\d+)$', 'views.successful_delivery', name='devilry-student-successful-delivery'),
)
