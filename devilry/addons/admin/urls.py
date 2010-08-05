from django.conf.urls.defaults import *


generic_urls = []
for x in ('node', 'subject', 'period'):
    generic_urls += [
        url(r'^%ss/(?P<obj_id>\d+)/edit$' % x, 'views.edit_%s' % x,
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

    url(r'^assignments/$',
        'views.list_assignments', name='devilry-admin-list_assignments'),
    url(r'^assignments/(?P<assignment_id>\d+)/edit$',
        'views.edit_assignment', name='devilry-admin-edit_assignment'),
    url(r'^assignments/(?P<assignment_id>\d+)/successful-save$',
        'views.edit_assignment',
        name = 'devilry-admin-edit_assignment-success',
        kwargs = {'successful_save':True}),
    url(r'^assignments/create$',
        'views.edit_assignment', name='devilry-admin-create_assignment'),
    url(r'^assignments/(?P<assignment_id>\d+)/delete$',
        'views.assignment.delete_assignment',
        name='devilry-admin-delete_assignment'),

    url(r'^assignments/(?P<assignment_id>\d+)/group/edit/(?P<assignmentgroup_id>\d+)$',
        'views.edit_assignmentgroup',
        name='devilry-admin-edit_assignmentgroup'),
    url(r'^assignments/(?P<assignment_id>\d+)/group/successful-save/(?P<assignmentgroup_id>\d+)$',
        'views.edit_assignmentgroup',
        name='devilry-admin-edit_assignmentgroup-success',
        kwargs = {'successful_save':True}),
    url(r'^assignments/(?P<assignment_id>\d+)/group/create$', 'views.edit_assignmentgroup',
        name='devilry-admin-create_assignmentgroup'),
    #url(r'^assignmentgroups/$', 'views.list_assignmentgroups',
        #name='devilry-admin-list_assignmentgroups'),

    url(r'^autocomplete-nodename$', 'views.json.nodename_json',
        name='admin-autocomplete-nodename'),
    url(r'^autocomplete-subjectname$', 'views.json.subjectname_json',
        name='admin-autocomplete-subjectname'),
    url(r'^autocomplete-periodname$', 'views.json.periodname_json',
        name='admin-autocomplete-periodname'),
    url(r'^autocomplete-assignmentname$', 'views.json.assignmentname_json',
        name='admin-autocomplete-assignmentname'),

    url(r'^autocomplete-nodename.js$', 'views.json.nodename_json_js',
        name='admin-autocomplete-nodename.js'),
    url(r'^autocomplete-subjectname.js$', 'views.json.subjectname_json_js',
        name='admin-autocomplete-subjectname.js'),
    url(r'^autocomplete-periodname.js$', 'views.json.periodname_json_js',
        name='admin-autocomplete-periodname.js'),
    url(r'^autocomplete-assignmentname.js$', 'views.json.assignmentname_json_js',
        name='admin-autocomplete-assignmentname.js'),

    url(r'^assignmentgroups/create-assignmentgroups/(?P<assignment_id>\d+)$',
        'views.create_assignmentgroups', name='devilry-admin-create_assignmentgroups'),
    url(r'^assignmentgroups/save-assignmentgroups/(?P<assignment_id>\d+)$',
        'views.save_assignmentgroups', name='devilry-admin-save_assignmentgroups'),
    *generic_urls
)
