from django.conf.urls.defaults import *



urlpatterns = patterns('devilry.addons.student',
    url(r'^choose-assignment/$', 'views.choose_assignment', name='devilry-student-choose_assignment'),
    url(r'^show-delivery/(?P<delivery_id>\d+)$', 'views.show_delivery', name='devilry-student-show_delivery'),
    url(r'^add-delivery/(?P<assignment_group_id>\d+)$', 'views.add_delivery', name='devilry-student-add_delivery'),
    url(r'^successful-delivery/(?P<assignment_group_id>\d+)$', 'views.successful_delivery', name='devilry-student-successful_delivery'),
    url(r'^show-history/$', 'views.show_history', name='devilry-student-show_history'),
    url(r'^show-assignmentgroup/(?P<assignmentgroup_id>\d+)$', 'views.show_assignmentgroup', name='devilry-student-show_assignmentgroup'),

)
