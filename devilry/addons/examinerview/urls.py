from django.conf.urls.defaults import *



urlpatterns = patterns('devilry.addons.examinerview',
    url(r'^$',
        'views.main', name='main'),

    url(r'^show-assignmentgroup/(?P<assignmentgroup_id>\d+)$',
        'views.show_assignmentgroup', name='show-assignmentgroup'),

    url(r'^list-deliveries/$',
        'views.list_deliveries', name='list-deliveries'),
    url(r'^show-delivery/(?P<delivery_id>\d+)$',
        'views.show_delivery', name='show-delivery'),
    url(r'^correct-delivery/(?P<delivery_id>\d+)$',
        'views.correct_delivery', name='correct-delivery'),
    url(r'^successful-delivery/(?P<delivery_id>\d+)$',
        'views.successful_delivery', name='successful-delivery'),

    url(r'^list_assignmentgroups/(?P<assignment_id>\d+)$',
        'views.list_assignmentgroups', name='list-assignmentgroups'),
    
    url(r'^list_assignments/$',
        'views.list_assignments', name='list-assignments'),

    url(r'^download-file/(?P<filemeta_id>\d+)$',
        'views.download_file', name='download-file'),
                           
)
