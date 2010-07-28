from django.conf.urls.defaults import *


generic_urls = []
for x in ('node', 'subject', 'period', 'assignmentgroup'):
    generic_urls += [
        url(r'^%ss/edit/(?P<obj_id>\d+)$' % x, 'views.edit_%s' % x,
            name='devilry-admin-edit_%s' % x),
        url(r'^%ss/successful-save/(?P<obj_id>\d+)$' % x, 'views.edit_%s' % x,
            name='devilry-admin-edit_%s-success' % x,
            kwargs = {'successful_save':True}),
        url(r'^%ss/create$' % x, 'views.edit_%s' % x,
            name='devilry-admin-create_%s' % x),
        url(r'^%ss/$' % x, 'views.list_%ss' % x,
            name='devilry-admin-list_%ss' % x)
        ]

urlpatterns = patterns('devilry.addons.admin',
    url(r'^$', 'views.main', name='devilry-admin-main'),

    url(r'^assignments/edit/(?P<assignment_id>\d+)$',
        'views.edit_assignment', name='devilry-admin-edit_assignment'),
    url(r'^assignments/successful-save/(?P<assignment_id>\d+)$',
        'views.edit_assignment',
        name = 'devilry-admin-edit_assignment-success',
        kwargs = {'successful_save':True}),
    url(r'^assignments/create$',
        'views.edit_assignment', name='devilry-admin-create_assignment'),
    url(r'^assignments/',
        'views.list_assignments', name='devilry-admin-list_assignments'),

    url(r'^assignmentgroups/create-assignmentgroups/(?P<assignment_id>\d+)$',
        'views.create_assignmentgroups', name='devilry-admin-create_assignmentgroups'),
    url(r'^assignmentgroups/save-assignmentgroups/(?P<assignment_id>\d+)$',
        'views.save_assignmentgroups', name='devilry-admin-save_assignmentgroups'),
    *generic_urls
)
