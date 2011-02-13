from django.conf.urls.defaults import *


# Node, Subject, Period and Assignment has exactly the same url-format
generic_urls = []
for clsname in ['node', 'subject', 'period', 'assignment']:
    generic_urls += [
        url(r'^%(clsname)ss/(?P<%(clsname)s_id>\d+)/edit$' % vars(),
            'views.%(clsname)s.edit_%(clsname)s' % vars(),
            name='devilry-admin-edit_%(clsname)s' % vars()),
        url(r'^%(clsname)ss/create$' % vars(),
            'views.%(clsname)s.edit_%(clsname)s' % vars(),
            name='devilry-admin-create_%(clsname)s' % vars()),
        url(r'^%(clsname)ss/deletemany$' % vars(),
            'views.%(clsname)s.delete_many%(clsname)ss' % vars(),
            name='devilry-admin-delete_many%(clsname)ss' % vars()),
        url(r'^%(clsname)ss/$' % vars(),
            'views.%(clsname)s.list_%(clsname)ss' % vars(),
            name='devilry-admin-list_%(clsname)ss' % vars()),
        url(r'^%(clsname)ss/json$' % vars(),
            'views.%(clsname)s.list_%(clsname)ss_json' % vars(),
            name='devilry-admin-list_%(clsname)ss_json' % vars()),
        ]

urlpatterns = patterns('devilry.addons.admin',
    url(r'^assignments/(?P<assignment_id>\d+)/group/edit/(?P<assignmentgroup_id>\d+)$',
        'views.assignmentgroup.edit_assignmentgroup',
        name='devilry-admin-edit_assignmentgroup'),
    url(r'^assignments/(?P<assignment_id>\d+)/group/successful-save/(?P<assignmentgroup_id>\d+)$',
        'views.assignmentgroup.edit_assignmentgroup',
        name='devilry-admin-edit_assignmentgroup-success',
        kwargs = {'successful_save':True}),
    url(r'^assignments/(?P<assignment_id>\d+)/group/create$',
        'views.assignmentgroup.edit_assignmentgroup',
        name='devilry-admin-create_assignmentgroup'),
    url(r'^assignments/(?P<assignment_id>\d+)/group/deletemany$',
        'views.assignmentgroup.delete_manyassignmentgroups',
        name='devilry-admin-delete_manyassignmentgroups'),

    url(r'^assignments/(?P<assignment_id>\d+)/create-assignmentgroups$',
        'views.assignmentgroup.create_assignmentgroups',
        name='devilry-admin-create_assignmentgroups'),
    url(r'^assignments/(?P<assignment_id>\d+)/save-assignmentgroups$',
        'views.assignmentgroup.save_assignmentgroups',
        name='devilry-admin-save_assignmentgroups'),

    url(r'^assignments/(?P<assignment_id>\d+)/set-examiners$',
        'views.assignmentgroup.set_examiners',
        name='devilry-admin-set_examiners'),
    url(r'^assignments/(?P<assignment_id>\d+)/random-dist-examiners$',
        'views.assignmentgroup.random_dist_examiners',
        name='devilry-admin-random_dist_examiners'),
    url(r'^assignments/(?P<assignment_id>\d+)/copy-groups$',
        'views.assignmentgroup.copy_groups',
        name='devilry-admin-copy_groups'),
    url(r'^assignments/(?P<assignment_id>\d+)/create-deadline$',
        'views.assignmentgroup.create_deadline',
        name='devilry-admin-create_deadline'),
    url(r'^assignments/(?P<assignment_id>\d+)/clear-deadlines$',
        'views.assignmentgroup.clear_deadlines',
        name='devilry-admin-clear_deadlines'),

    url(r'^assignments/(?P<assignment_id>\d+)/open-many-groups$',
        'views.assignmentgroup.open_many_groups',
        name='devilry-admin-open_many_groups'),
    url(r'^assignments/(?P<assignment_id>\d+)/close-many-groups$',
        'views.assignmentgroup.close_many_groups',
        name='devilry-admin-close_many_groups'),

    url(r'^assignments/(?P<assignment_id>\d+)/publish-many-groups$',
        'views.assignmentgroup.publish_many_groups',
        name='devilry-admin-publish_many_groups'),

    url(r'^assignments/(?P<assignment_id>\d+)/download_assignment_collection_as_tar$',
        'views.assignmentgroup.download_assignment_collection',
        kwargs={"archive_type":"tar"},
        name='devilry-admin-download_assignment_collection_as_tar'),

    url(r'^assignments/(?P<assignment_id>\d+)/download_assignment_collection_as_zip$',
        'views.assignmentgroup.download_assignment_collection',
        kwargs={"archive_type":"zip"},
        name='devilry-admin-download_assignment_collection_as_zip'),

    url(r'^assignments/(?P<assignment_id>\d+)/assignmentgroups-json$',
        'views.assignment.assignmentgroups_json',
        name='devilry-admin-assignmentgroups-json'),


    *generic_urls
)
