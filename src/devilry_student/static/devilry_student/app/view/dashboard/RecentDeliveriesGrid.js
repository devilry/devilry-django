Ext.define('devilry_student.view.dashboard.RecentDeliveriesGrid', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.recentdeliveriesgrid',
    cls: 'devilry_student_recentdeliveriesgrid',
    requires: [
        'devilry_extjsextras.DatetimeHelpers'
    ],

    frame: false,
    border: 0,
    hideHeaders: true,
    store: 'RecentDeliveries',
    disableSelection: true,

    col1Tpl: [
        '<div class="ident"><a href="#/group/{delivery.group.id}/{delivery.id}">',
            '{delivery.subject.short_name} - {delivery.assignment.short_name} - #{delivery.number}',
        '</a></div>',
        '<div class="metainfo">',
            '<small class="muted offset_from_now">', gettext('Added {offset_from_now} ago'), '</small>',
        '</div>'
    ],

    initComponent: function() {
        var col1TplCompiled = Ext.create('Ext.XTemplate', this.col1Tpl);
        Ext.apply(this, {
            cls: 'bootstrap',
            columns: [{
                header: 'data',
                dataIndex: 'id',
                flex: 1,
                sortable: false,
                menuDisabled: true,
                renderer: function(value, m, recentDeliveryRecord) {
                    var offset_from_now = recentDeliveryRecord.get('time_of_delivery').offset_from_now;
                    return col1TplCompiled.apply({
                        delivery: recentDeliveryRecord.data,
                        offset_from_now: devilry_extjsextras.DatetimeHelpers.formatTimedeltaShort(offset_from_now)
                    });
                }
            }]
        });
        this.callParent(arguments);
    }
});
