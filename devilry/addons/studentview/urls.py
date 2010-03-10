from django.conf.urls.defaults import *



urlpatterns = patterns('devilry.addons.studentview',
    (r'^$', 'views.main'),
    (r'^list-assignmentgroups/$', 'views.list_assignmentgroups'),
    (r'^show-assignment-group/(?P<assignmentgroup_id>\d+)$', 'views.show_assignmentgroup'),

    (r'^list-deliveries/$', 'views.list_deliveries'),
    (r'^show-delivery/(?P<delivery_id>\d+)$', 'views.show_delivery'),
    (r'^add-delivery/(?P<assignment_group_id>\d+)$', 'views.add_delivery'),
    (r'^successful-delivery/(?P<delivery_id>\d+)$', 'views.successful_delivery'),
    (r'^show-history/$', 'views.show_history'),
)
