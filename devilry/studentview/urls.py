from django.conf.urls.defaults import *



urlpatterns = patterns('devilry.studentview',
    url(r'^list-assignmentgroups/$',
        'views.list_assignmentgroups', name='list-assignmentgroups'),
    url(r'^show-assignmentgroup/(?P<assignmentgroup_id>\d+)$',
        'views.show_assignmentgroup', name='show-assignmentgroup'),

    url(r'^list-deliveries/$',
        'views.list_deliveries', name='list-deliveries'),
    url(r'^show-delivery/(?P<delivery_id>\d+)$',
        'views.show_delivery', name='show-delivery'),
    url(r'^add-delivery/(?P<assignment_group_id>\d+)$',
        'views.add_delivery', name='add-delivery'),
    url(r'^successful-delivery/(?P<delivery_id>\d+)$',
        'views.successful_delivery', name='successful-delivery'),
)
