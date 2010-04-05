from django.conf.urls.defaults import *



urlpatterns = patterns('devilry.addons.student',
    # Delivery
    url(r'^add-delivery/$', 'views.add_delivery_choose_assignment', name='devilry-student-add_delivery_choose_assignment'),
    url(r'^add-delivery/(?P<assignment_group_id>\d+)$', 'views.add_delivery', name='devilry-student-add_delivery'),
    url(r'^successful-delivery/(?P<assignment_group_id>\d+)$', 'views.successful_delivery', name='devilry-student-successful_delivery'),

    # History
    url(r'^history/$', 'views.show_history', name='devilry-student-show_history'),
    url(r'^history/(?P<assignmentgroup_id>\d+)$', 'views.show_assignmentgroup', name='devilry-student-show_assignmentgroup'),
    url(r'^history/delivery/(?P<delivery_id>\d+)$', 'views.show_delivery', name='devilry-student-show_delivery'),

)
