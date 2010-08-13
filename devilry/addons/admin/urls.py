from django.utils.translation import ugettext as _
from django.conf.urls.defaults import *


# Node, Subject, Period and Assignment has exactly the same url-format
generic_urls = []
for clsname in ('node', 'subject', 'period', 'assignment'):
    generic_urls += [
        url(r'^%(clsname)ss/(?P<%(clsname)s_id>\d+)/edit$' % vars(),
            'views.edit_%(clsname)s' % vars(),
            name='devilry-admin-edit_%(clsname)s' % vars()),
        url(r'^%(clsname)ss/create$' % vars(),
            'views.edit_%(clsname)s' % vars(),
            name='devilry-admin-create_%(clsname)s' % vars()),
        url(r'^%(clsname)ss/deletemany$' % vars(),
            'views.delete_many%(clsname)ss' % vars(),
            name='devilry-admin-delete_many%(clsname)ss' % vars()),
        url(r'^autocomplete-%(clsname)sname$' % vars(),
            'views.json.%(clsname)s_json' % vars(),
            name='admin-autocomplete-%(clsname)sname' % vars()),
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
        'views.delete_manyassignmentgroups',
        name='devilry-admin-delete_manyassignmentgroups'),

    url(r'^assignments/(?P<assignment_id>\d+)/create-assignmentgroups$',
        'views.assignmentgroup.create_assignmentgroups',
        name='devilry-admin-create_assignmentgroups'),
    url(r'^assignments/(?P<assignment_id>\d+)/save-assignmentgroups$',
        'views.assignmentgroup.save_assignmentgroups',
        name='devilry-admin-save_assignmentgroups'),

    url(r'^autocomplete-assignmentgroupname/(?P<assignment_id>\d+)$',
        'views.json.assignmentgroup_json',
        name='admin-autocomplete-assignmentgroupname'),

    url(r'^assignments/(?P<assignment_id>\d+)/set-examiners$',
        'views.assignmentgroup.set_examiners',
        name='devilry-admin-set_examiners'),
    url(r'^assignments/(?P<assignment_id>\d+)/copy-groups$',
        'views.assignmentgroup.copy_groups',
        name='devilry-admin-copy_groups'),
    url(r'^assignments/(?P<assignment_id>\d+)/create-deadline$',
        'views.assignmentgroup.create_deadline',
        name='devilry-admin-create_deadline'),
    url(r'^assignments/(?P<assignment_id>\d+)/clear-deadlines$',
        'views.assignmentgroup.clear_deadlines',
        name='devilry-admin-clear_deadlines'),

    *generic_urls
)
