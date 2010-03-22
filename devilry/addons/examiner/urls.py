from django.conf.urls.defaults import *



urlpatterns = patterns('devilry.addons.examiner',
    url(r'^choose-assignment$', 'views.choose_assignment', name='devilry-examiner-choose_assignment'),

    url(r'^show-assignmentgroup/(?P<assignmentgroup_id>\d+)$',
        'views.show_assignmentgroup', name='devilry-examiner-show_assignmentgroup'),

    url(r'^correct-delivery/(?P<delivery_id>\d+)$', 'views.correct_delivery', name='devilry-examiner-correct_delivery'),
    url(r'^list_assignmentgroups/(?P<assignment_id>\d+)$', 'views.list_assignmentgroups', name='devilry-examiner-list_assignmentgroups'),
)
