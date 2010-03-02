from django.conf.urls.defaults import *


generic_urls = []
for x in ('node', 'subject', 'period', 'assignment'):
    generic_urls += [
        url(r'^%ss/edit/(?P<node_id>\d+)$' % x,
            'views.edit_%s' % x, name='edit-%s' % x),
        url(r'^%ss/add$' % x,
            'views.edit_%s' % x, name='add-%s' % x),
        url(r'^%ss/$' % x,
            'views.list_%ss' % x, name='list-%ss' % x)]

urlpatterns = patterns('devilry.studentview',
    url(r'^admin/$', 'views.admin', name='admin'),
    url(r'^logout$', 'views.logout_view', name='logout'),
    url(r'^login$', 'views.login_view', name='login'),

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
    *generic_urls
)
