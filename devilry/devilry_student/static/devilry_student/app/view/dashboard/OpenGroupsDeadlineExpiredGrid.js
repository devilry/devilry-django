Ext.define('devilry_student.view.dashboard.OpenGroupsDeadlineExpiredGrid', {
    extend: 'devilry_student.view.dashboard.OpenGroupsDeadlineNotExpiredGrid',
    alias: 'widget.opengroups_deadline_expired_grid',
    cls: 'devilry_student_opengroupsgrid expired',
    store: 'OpenGroupsDeadlineExpired',

    titleTpl: [
        '<div class="ident"><a href="#/group/{group.id}/@@add-delivery">',
            '{group.subject.short_name} - {group.assignment.long_name}',
        '</a></div>'
    ]
});
