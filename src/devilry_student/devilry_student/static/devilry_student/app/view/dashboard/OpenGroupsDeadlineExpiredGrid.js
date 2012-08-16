Ext.define('devilry_student.view.dashboard.OpenGroupsDeadlineExpiredGrid', {
    extend: 'devilry_student.view.dashboard.OpenGroupsDeadlineNotExpiredGrid',
    alias: 'widget.opengroups_deadline_expired_grid',
    cls: 'devilry_student_opengroupsgrid expired',
    store: 'OpenGroupsDeadlineExpired',


    metaTpl: [
        '<div>',
            '<small class="deliveries"><em>{deliveries_term}:</em> {group.deliveries}</small>',
            '<small class="divider">,&nbsp;&nbsp;</small>',
            '<small class="deadline"><em>{deadline_term}:</em> {group.active_deadline.deadline}</small>',
        '</div>',
        '<div><span class="danger">',
            gettext('{deadline_term} was {offset_from_deadline} ago'),
        '</span></div>'
    ],
});
