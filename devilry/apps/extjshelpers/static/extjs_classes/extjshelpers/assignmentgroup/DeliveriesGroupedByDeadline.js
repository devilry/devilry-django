Ext.define('devilry.extjshelpers.assignmentgroup.DeliveriesGroupedByDeadline', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.deliveriesgroupedbydeadline',
    cls: 'widget-deliveriesgroupedbydeadline',
    requires: [
        'devilry.administrator.models.Deadline',
        'devilry.administrator.models.Delivery',
        'devilry.administrator.models.StaticFeedback',
        'devilry.examiner.models.Deadline',
        'devilry.examiner.models.Delivery',
        'devilry.examiner.models.StaticFeedback',
        'devilry.student.models.Deadline',
        'devilry.student.models.Delivery',
        'devilry.student.models.StaticFeedback',

        'devilry.extjshelpers.RestFactory',
        'devilry.extjshelpers.assignmentgroup.DeliveriesGrid',
        'devilry.extjshelpers.assignmentgroup.DeliveriesPanel',
        'devilry.extjshelpers.assignmentgroup.CreateNewDeadlineWindow'
    ],

    title: 'Deliveries grouped by deadline',

    layout: {
        type: 'accordion'
    },

    config: {
        role: undefined,
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
        var deadlinestore = devilry.extjshelpers.RestFactory.createStore(this.role, 'Deadline', {
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

                if(index === 0) {
                    var is_open = this.assignmentgroup_recordcontainer.record.get('is_open');
                    if(deliveryRecords.length === 0 && deadlineRecords[0].get('deadline') < Ext.Date.now() && is_open) {
                        this._onExpiredNoDeliveries();
                    }
                }

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
            assignmentgroup_recordcontainer: this.assignmentgroup_recordcontainer,
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
            deadlinemodel: Ext.String.format('devilry.{0}.models.Deadline', this.role),
            onSaveSuccess: function(record) {
                this.close();
                me.loadAllDeadlines();
            }
        });
        createDeadlineWindow.show();
    },


    /**
     * @private
     */
    _onExpiredNoDeliveries: function() {
        var win = Ext.MessageBox.show({
            title: 'This group has no deliveries, and their active deadline has expired',
            msg: '<p>Would you like to give the group a new deadline?</p><ul>' +
                '<li>Choose <strong>yes</strong> to create a new deadline</li>' +
                '<li>Choose <strong>no</strong> to close the group. This fails the student on this assignment. You can re-open the group at any time.</li>' +
                '<li>Choose <strong>cancel</strong> to close this window without doing anything.</li>' +
                '</ul>',
            buttons: Ext.Msg.YESNOCANCEL,
            scope: this,
            closable: false,
            fn: function(buttonId) {
                if(buttonId == 'yes') {
                    this.onCreateNewDeadline()
                } else if (buttonId == 'no') {
                    devilry.extjshelpers.assignmentgroup.IsOpen.closeGroup(this.assignmentgroup_recordcontainer);
                }
            }
        });
    },
});
