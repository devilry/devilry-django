Ext.define('devilry.extjshelpers.assignmentgroup.DeliveriesGrid', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.deliveriesgrid',
    cls: 'widget-deliveriesgrid',
    hideHeaders: true, // Hide column header
    mixins: [
        'devilry.extjshelpers.AddPagerIfNeeded'
    ],
    requires: [
        'devilry_extjsextras.DatetimeHelpers'
    ],

    rowTpl: Ext.create('Ext.XTemplate',
        '<div class="bootstrap" style="white-space:normal; line-height: 1.5em !important;">',
            '<div>',
                '<span class="delivery_number">{delivery.number}:</span> ',
                '<tpl if="assignmentgroup.parentnode__delivery_types === 1">',
                    '<span class="not_in_devilry">',
                        gettext('Non-electronic delivery'),
                    '</span>',
                '<tpl else>',
                    '<span class="time_of_delivery">{[this.formatDatetime(values.delivery.time_of_delivery)]}</span>',
                    '<tpl if="delivery.delivery_type == 0">',
                        '<div class="afterdeadline">',
                            '<tpl if="delivery.time_of_delivery &gt; deadline.deadline">',
                                 ' <span class="label label-important">',
                                    gettext('After deadline'),
                                 '</span>',
                            '</tpl>',
                        '</div>',
                    '</tpl>',
                '</tpl>',
            '</div>',
            '<tpl if="delivery.delivery_type == 2">',
                '<div><span class="label label-inverse">',
                    interpolate(gettext('From previous %(period_term)s'), {
                        period_term: gettext('period')
                    }, true),
                '</span></div>',
            '</tpl>',
            '<div class="feedback">',
                '<tpl if="feedback">',
                    '<span class="{[this.getFeedbackClass(values.feedback)]}">',
                        '{[this.getPassingLabel(values.feedback)]} ({feedback.grade})',
                    '</span>',
                '</tpl>',
                '<tpl if="hasLatestFeedback">',
                    ' <span class="label label-success">',
                        gettext('active feedback'),
                    '</span>',
                '</tpl>',
            '</div>',
        '</div>', {
            formatDatetime:function (dt) {
                return devilry_extjsextras.DatetimeHelpers.formatDateTimeShort(dt);
            },
            getFeedbackClass:function (feedback) {
                return feedback.is_passing_grade? 'text-success': 'text-warning';
            },
            getPassingLabel:function (feedback) {
                return feedback.is_passing_grade? gettext('Passed'): gettext('Failed');
            }
        }
    ),

    /**
     * @cfg {Object} [assignmentgroup_recordcontainer]
     * help
     */

    /**
     * @cfg {Object} [deadlineRecord]
     */

    /**
     * @cfg {Object} [delivery_recordcontainer]
     * A {@link devilry.extjshelpers.SingleRecordContainer} for Delivery.
     * The record is changed when a user selects a delivery.
     */


    initComponent: function() {
        var me = this;
        Ext.apply(this, {
            border: false,
            columns: [{
                header: 'Data',
                dataIndex: 'id',
                flex: 1,
                renderer: function(value, metaData, deliveryrecord) {
                    //console.log(deliveryrecord.data);
                    var staticfeedbackStore = deliveryrecord.staticfeedbacks();
                    return this.rowTpl.apply({
                        delivery: deliveryrecord.data,
                        hasLatestFeedback: deliveryrecord.hasLatestFeedback,
                        deadline: this.deadlineRecord.data,
                        assignmentgroup: this.assignmentgroup_recordcontainer.record.data,
                        feedback: staticfeedbackStore.count() > 0? staticfeedbackStore.data.items[0].data: undefined
                    });
                }
            }],
            listeners: {
                scope: this,
                select: this.onSelectDelivery
            }
        });

        this.addPagerIfNeeded();
        this.callParent(arguments);
    },

    /**
     * @private
     */
    onSelectDelivery: function(grid, deliveryRecord) {
        var allGrids = this.up('deliveriesgroupedbydeadline').query('deliveriesgrid');
        Ext.each(allGrids, function(grid, index) {
            if(grid !== this) {
                grid.getSelectionModel().deselectAll();
            }
        }, this);
        this.delivery_recordcontainer.setRecord(deliveryRecord);
    }
});
