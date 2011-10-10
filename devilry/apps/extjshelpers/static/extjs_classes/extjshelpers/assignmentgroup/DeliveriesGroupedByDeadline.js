Ext.define('devilry.extjshelpers.assignmentgroup.DeliveriesGroupedByDeadline', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.deliveriesgroupedbydeadline',
    cls: 'widget-deliveriesgroupedbydeadline',
    requires: [
        'devilry.extjshelpers.RestFactory',
        'devilry.administrator.models.StaticFeedback',
        'devilry.administrator.models.Delivery',
        'devilry.administrator.models.Deadline',
        'devilry.extjshelpers.assignmentgroup.DeliveriesGrid',
        'devilry.extjshelpers.assignmentgroup.DeliveriesPanel',
        'devilry.extjshelpers.assignmentgroup.CreateNewDeadlineWindow'
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
        this.isLoading = true;
        this.assignmentgroup_recordcontainer.on('setRecord', this.loadAllDeadlines, this);
    },

    initComponent: function() {
        Ext.apply(this, {
            bbar: [{
                xtype: 'button',
                text: 'New deadline',
                iconCls: 'icon-add-16',
                listeners: {
                    scope: this,
                    click: this.onCreateNewDeadline
                }
            }]
        });
        this.callParent(arguments);
        this.on('render', function() {
            Ext.defer(function() {
                this.addLoadMask();
            }, 100, this);
        }, this);
    },


    /**
     * @private
     */
    addLoadMask: function() {
        if(this.rendered && this.isLoading) {
            this.getEl().mask('Loading deliveries ...');
        }
    },

    /**
     * @private
     */
    loadAllDeadlines: function() {
        this.isLoading = true;
        this._tmp_deliveriespanels = [];
        this.addLoadMask();
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
    handleSingleDeadline: function(deadlineRecord, index, deadlineRecords) {
        var deliveriesStore = deadlineRecord.deliveries();
        //deliveriesStore.pageSize = 1; // Uncomment to test paging
        deliveriesStore.load({
            scope: this,
            callback: function(deliveryRecords) {
                if(deliveryRecords.length === 0) {
                    this.addDeliveriesPanel(deadlineRecords, deadlineRecord, deliveriesStore);
                } else {
                    this.findLatestFeebackInDeadline(deadlineRecords, deadlineRecord, deliveriesStore, deliveryRecords)
                }
            }
        });
    },

    findLatestFeebackInDeadline: function(deadlineRecords, deadlineRecord, deliveriesStore, deliveryRecords) {
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
                        this.sortAllStaticFeedbacks(allStaticFeedbacks);
                        var activeFeedback = allStaticFeedbacks[0];
                        this.addDeliveriesPanel(deadlineRecords, deadlineRecord, deliveriesStore, activeFeedback);
                    }
                }
            })
        }, this);
    },

    /**
     * @private
     */
    sortAllStaticFeedbacks: function(allStaticFeedbacks) {
        allStaticFeedbacks.sort(function(a, b) {
            if(a.data.save_timestamp > b.data.save_timestamp) {
                return -1;
            } else if(a.data.save_timestamp === b.data.save_timestamp) {
                return 0;
            } else {
                return 1;
            }
        });
    },

    /**
     * @private
     */
    addDeliveriesPanel: function(deadlineRecords, deadlineRecord, deliveriesStore, activeFeedback) {
        this._tmp_deliveriespanels.push({
            xtype: 'deliveriespanel',
            delivery_recordcontainer: this.delivery_recordcontainer,
            deadlineRecord: deadlineRecord,
            deliveriesStore: deliveriesStore,
            activeFeedback: activeFeedback
        });

        if(this._tmp_deliveriespanels.length === deadlineRecords.length) {
            this.sortDeliveryPanels();
            this.add(this._tmp_deliveriespanels);
            this.getEl().unmask();
            this.isLoading = false;
        }
    },

    /**
     * @private
     * Sort delivery panels, since they are added on response from an
     * asynchronous operation. Sorted descending by deadline datetime.
     */
    sortDeliveryPanels: function() {
        this._tmp_deliveriespanels.sort(function(a, b) {
            if(a.deadlineRecord.data.deadline > b.deadlineRecord.data.deadline) {
                return -1;
            } else if(a.deadlineRecord.data.deadline === b.deadlineRecord.data.deadline) {
                return 0;
            } else {
                return 1;
            }
        });
    },


    /**
     * @private
     */
    onCreateNewDeadline: function() {
        var me = this;
        var createDeadlineWindow = Ext.widget('createnewdeadlinewindow', {
            assignmentgroupid: this.assignmentgroup_recordcontainer.record.data.id,
            deadlinemodel: 'devilry.administrator.models.Deadline',
            onSaveSuccess: function(record) {
                this.close();
                me.loadAllDeadlines();
            }
        });
        createDeadlineWindow.show();
    }
});
