Ext.define('devilry_student.view.dashboard.OpenGroupsDeadlineNotExpiredGrid', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.opengroups_deadline_not_expired_grid',
    cls: 'devilry_student_opengroupsgrid not_expired',
    requires: [
        'devilry_extjsextras.DatetimeHelpers'
    ],

    frame: false,
    border: 0,
    hideHeaders: true,
    store: 'OpenGroupsDeadlineNotExpired',
    disableSelection: true,

    titleTpl: [
        '<div class="ident"><strong><a href="#/group/{group.id}/@@add-delivery">',
            '{group.subject.short_name} - {group.assignment.long_name}',
        '</a></strong></div>'
    ],

    metaTpl: [
        '<div class="metainfo">',
            '<small class="deliveries muted"><em>{deliveries_term}:</em> {group.deliveries}</small>',
            '<small class="divider muted">,&nbsp;&nbsp;</small>',
            '<small class="deadline muted"><em>{deadline_term}:</em> {group.active_deadline.deadline}</small>',
            ' ',
            '<tpl if="deadline_expired">',
                '<small class="deadlinedelta text-warning">({offset_from_deadline})</small>',
            '<tpl else>',
                '<small class="deadlinedelta text-success">({offset_from_deadline})</small>',
            '</tpl>',
        '</div>'
    ],

    initComponent: function() {
        var tpl = this.titleTpl.concat(this.metaTpl);
        var col1TplCompiled = Ext.create('Ext.XTemplate', tpl);
        Ext.apply(this, {
            cls: 'bootstrap',
            columns: [{
                header: 'data',
                dataIndex: 'id',
                flex: 1,
                sortable: false,
                menuDisabled: true,
                renderer: function(value, m, openGroupRecord) {
                    var deadline = openGroupRecord.get('active_deadline');
                    return col1TplCompiled.apply({
                        group: openGroupRecord.data,
                        deadline_term: gettext('Deadline'),
                        deliveries_term: gettext('Deliveries'),
                        deadline_expired: deadline.deadline_expired,
                        offset_from_deadline: devilry_extjsextras.DatetimeHelpers.formatTimedeltaRelative(
                            deadline.offset_from_deadline,
                            !deadline.deadline_expired)
                    });
                }
            }]
        });
        this.callParent(arguments);
    }
});
