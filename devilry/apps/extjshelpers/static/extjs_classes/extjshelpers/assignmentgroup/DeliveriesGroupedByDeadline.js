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

    autoScroll: true,
//    style: 'border-right: 1px solid #ddd !important; border-top: 1px solid #ddd !important;',
    border: 1,

    /**
    * @cfg {string} [role]
    */
    role: undefined,

    /**
    * @cfg {object} [assignmentgroup_recordcontainer]
    * AssignmentGroup record container. The view is reloaded on the setRecord
    * event.
    */
    assignmentgroup_recordcontainer: undefined,

    /**
    * @cfg {object} [delivery_recordcontainer]
    * A {@link devilry.extjshelpers.SingleRecordContainer} for Delivery.
    * The record is changed when a user selects a delivery.
    */
    delivery_recordcontainer: undefined,

    constructor: function(config) {
        this.addEvents('loadComplete');
        this.callParent(arguments);
    },

    initComponent: function() {
        this.isLoading = true;
        this.assignmentgroup_recordcontainer.on('setRecord', this._onLoadAssignmentGroup, this);
        if(this.assignmentgroup_recordcontainer.record) {
            this._onLoadAssignmentGroup();
        }

        this.callParent(arguments);
        this.on('render', function() {
            Ext.defer(function() {
                this.addLoadMask();
            }, 100, this);
        }, this);
    },

    _onLoadAssignmentGroup: function(groupRecordContainer) {
        var groupRecord = groupRecordContainer.record;
        this.loadAllDeadlines();
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
        this._allDeliveries = [];
        this._tmp_deliveriespanels = [];
        this._tmp_active_feedbacks = [];
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
        deliveriesStore.pageSize = 1000;
        deliveriesStore.load({
            scope: this,
            callback: function(deliveryRecords) {
                if(index === 0) {
                    this._handleLatestDeadline(deadlineRecords[0], deliveryRecords);
                }

                if(deliveryRecords.length === 0) {
                    this.addDeliveriesPanel(deadlineRecords, deadlineRecord, deliveriesStore);
                } else {
                    this.findLatestFeebackInDeadline(deadlineRecords, deadlineRecord, deliveriesStore, deliveryRecords);
                }
            }
        });
    },

    _handleLatestDeadline: function(deadlineRecord, deliveryRecords) {
        var is_open = this.assignmentgroup_recordcontainer.record.get('is_open');
        if(this.role !== 'student' && deliveryRecords.length === 0 && deadlineRecord.get('deadline') < Ext.Date.now() && is_open) {
            this.fireEvent('expiredNoDeliveries');
        }
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
                        this._sortStaticfeedbacks(allStaticFeedbacks);
                        var activeFeedback = allStaticFeedbacks[0];
                        this.addDeliveriesPanel(deadlineRecords, deadlineRecord, deliveriesStore, activeFeedback);
                    }
                }
            });
        }, this);
    },

    /**
     * @private
     */
    _sortStaticfeedbacks: function(allStaticFeedbacks) {
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
        this._tmp_active_feedbacks.push(activeFeedback);

        this._cacheAllDeliveriesInStore(deliveriesStore);
        if(this._tmp_deliveriespanels.length === deadlineRecords.length) {
            this._sortDeliveryPanels();
            this._findAndMarkActiveFeedback();
            this.add(this._tmp_deliveriespanels);
            this.getEl().unmask();
            this.isLoading = false;
            this.fireEvent('loadComplete', this);
            this._onLoadComplete();
        }
    },

    _onLoadComplete:function () {
        var group = this.assignmentgroup_recordcontainer.record;
        if(group.get('parentnode__delivery_types') !== 1) {
            this.add({
                xtype: 'button',
                scale: 'medium',
                text: '<i class="icon-time"></i> ' + gettext('New deadline'),
                cls: 'bootstrap',
                listeners: {
                    scope: this,
                    click:function () {
                        this.fireEvent('createNewDeadline');
                    }
                }
            });
        }
    },

    _cacheAllDeliveriesInStore: function(store) {
        Ext.each(store.data.items, function(deliveryRecord, index) {
            this._allDeliveries.push(deliveryRecord);
        }, this);
    },

    _findAndMarkActiveFeedback: function() {
        this._sortStaticfeedbacks(this._tmp_active_feedbacks);
        this.latestStaticFeedbackRecord = this._tmp_active_feedbacks[0];
        if(!this.latestStaticFeedbackRecord) {
            return;
        }
        Ext.each(this._tmp_deliveriespanels, function(deliveriespanel, index) {
            Ext.each(deliveriespanel.deliveriesStore.data.items, function(deliveryRecord, index) {
                if(deliveryRecord.data.id === this.latestStaticFeedbackRecord.get('delivery')) {
                    deliveryRecord.hasLatestFeedback = true;
                }
            }, this);
        }, this);
    },

    /**
     * @private
     * Sort delivery panels, since they are added on response from an
     * asynchronous operation. Sorted descending by deadline datetime.
     */
    _sortDeliveryPanels: function() {
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

    getLatestDelivery: function() {
        return this._allDeliveries[0];
    },

    selectDelivery: function(deliveryid) {
        Ext.each(this.items.items, function(deliveriespanel) {
            var index = deliveriespanel.deliveriesStore.find('id', deliveryid);
            if(index !== -1) {
                var deliveriesgrid = deliveriespanel.down('deliveriesgrid');
//                if(deliveriespanel.collapsed) {
//                    deliveriespanel.toggleCollapse();
//                }
                deliveriesgrid.getSelectionModel().select(index);
                return false; // break
            }
        }, this);
    }
});
