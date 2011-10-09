Ext.define('devilry.extjshelpers.assignmentgroup.DeliveriesGroupedByDeadline', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.deliveriesgroupedbydeadline',
    cls: 'widget-deliveriesgroupedbydeadline',
    requires: [
        'devilry.extjshelpers.RestFactory',
        'devilry.administrator.models.StaticFeedback',
        'devilry.administrator.models.Delivery',
        'devilry.administrator.models.Deadline',
        'devilry.extjshelpers.assignmentgroup.DeliveriesGrid'
    ],

    title: 'Deliveries grouped by deadline',

    layout: {
        type: 'accordion'
    },

    config: {
        assignmentgroup_recordcontainer: undefined,

        /**
         * @cfg
         * A {@link devilry.extjshelpers.SingleRecordContainer} for Delivery.
         * The record is changed when a user selects a delivery.
         */
        delivery_recordcontainer: undefined
    },

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
        this.assignmentgroup_recordcontainer.on('setRecord', this.loadAllDeadlines, this);
    },

    titleTpl: Ext.create('Ext.XTemplate',
        '<div class="deadline_title">',
        '    <div>Deadline: <span class="deadline">{deadline.deadline:date}</span></div>',
        '    <div>',
        '        Deliveries: <span class="number_of_deliveries">{deadline.number_of_deliveries}</span>',
        '        <tpl if="deadline.number_of_deliveries &gt; 0">{extra}</tpl>',
        '    </div>',
        '<div>'
    ),


    /**
     * @private
     */
    loadAllDeadlines: function() {
        this.removeAll();
        var deadlinestore = devilry.extjshelpers.RestFactory.createStore('administrator', 'Deadline', {
            filters: [{
                property: 'assignment_group',
                value: this.assignmentgroup_recordcontainer.record.data.id
            }]
        });
        deadlinestore.proxy.setDevilryOrderby(['-deadline']);
        deadlinestore.loadAll({
            scope: this,
            callback: this.onLoadAllDeadlines
        });
    },

    /**
     * @private
     */
    onLoadAllDeadlines: function(deadlineRecords) {
        Ext.each(deadlineRecords, this.handleSingleDeadline, this);
    },

    /**
     * @private
     */
    handleSingleDeadline: function(deadlineRecord, index) {
        var deliveriesStore = deadlineRecord.deliveries();
        //deliveriesStore.pageSize = 1; // Uncomment to test paging
        deliveriesStore.load({
            scope: this,
            callback: function(deliveryRecords) {
                this.findLatestFeebackInDeadline(deadlineRecord, deliveriesStore, deliveryRecords)
            }
        });
    },

    findLatestFeebackInDeadline: function(deadlineRecord, deliveriesStore, deliveryRecords) {
        var allStaticFeedbacks = [];
        var loadedStaticFeedbackStores = 0;
        Ext.each(deliveryRecords, function(deliveryRecord, index) {
            var staticfeedbackStore = deliveryRecord.staticfeedbacks();
            staticfeedbackStore.load({
                scope: this,
                callback: function(staticFeedbackRecords) {
                    loadedStaticFeedbackStores ++;
                    if(staticFeedbackRecords.length > 0) {
                        allStaticFeedbacks.push(staticFeedbackRecords[0]);
                    }
                    if(loadedStaticFeedbackStores === deliveryRecords.length) {
                        // TODO: Sort allStaticFeedbacks by save_timestamp and pick first
                        var activeFeedback = allStaticFeedbacks[0];
                        this.addDeadlineGrid(deadlineRecord, deliveriesStore, activeFeedback);
                    }
                }
            })
        }, this);
    },

    addDeadlineGrid: function(deadlineRecord, deliveriesStore, activeFeedback) {
        var extra = '(No feedback)';
        if(activeFeedback) {
            var extra = Ext.String.format('(Grade: {0} SEE TODO)', activeFeedback.data.grade);
        }
        this.add({
            xtype: 'panel',
            title: this.titleTpl.apply({
                deadline: deadlineRecord.data,
                extra: extra
            }),
            layout: 'fit',
            border: false,
            items: [{
                xtype: 'deliveriesgrid',
                delivery_recordcontainer: this.delivery_recordcontainer,
                store: deliveriesStore
            }]
        });
    }
});
