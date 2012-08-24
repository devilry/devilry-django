Ext.define('devilry_student.view.dashboard.OpenGroupsDeadlineExpiredGrid', {
    extend: 'devilry_student.view.dashboard.OpenGroupsDeadlineNotExpiredGrid',
    alias: 'widget.opengroups_deadline_expired_grid',
    cls: 'devilry_student_opengroupsgrid expired',
    store: 'OpenGroupsDeadlineExpired',

    titleTpl: [
        '<div><a href="#/group/{group.id}/@@add-delivery">',
            '{group.subject.short_name} - {group.assignment.long_name}',
        '</a></div>'
    ],

    metaTpl: [
        '<div>',
            '<small class="deliveries"><em>{deliveries_term}:</em> {group.deliveries}</small>',
            '<small class="divider">,&nbsp;&nbsp;</small>',
            '<small class="deadline danger">',
                gettext('{deadline_term} was {offset_from_deadline} ago'),
            '</small>',
        '</div>'
    ]
});
