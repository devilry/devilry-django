from django.conf.urls.defaults import *



urlpatterns = patterns('devilry.addons.examiner',
    url(r'^$', 'views.main', name='devilry-examiner-main'),

    url(r'^show-assignmentgroup/(?P<assignmentgroup_id>\d+)$',
        'views.show_assignmentgroup', name='devilry-examiner-show_assignmentgroup'),

    url(r'^list-deliveries/$', 'views.list_deliveries', name='devilry-examiner-list_deliveries'),
    url(r'^show-delivery/(?P<delivery_id>\d+)$', 'views.show_delivery', name='devilry-examiner-show_delivery'),
    url(r'^correct-delivery/(?P<delivery_id>\d+)$', 'views.correct_delivery', name='devilry-examiner-correct_delivery'),
    url(r'^list_assignmentgroups/(?P<assignment_id>\d+)$', 'views.list_assignmentgroups', name='devilry-examiner-list_assignmentgroups'),
    url(r'^list_assignments/$', 'views.list_assignments', name='devilry-examiner-list_assignments'),
    url(r'^download-file/(?P<filemeta_id>\d+)$', 'views.download_file', name='devilry-examiner-download_file'),
)
