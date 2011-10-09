Ext.define('devilry.extjshelpers.assignmentgroup.DeliveriesOnSingleGroupLoader', {
    requires: [
        'devilry.extjshelpers.RestFactory',
        'devilry.administrator.models.Delivery',
        'devilry.administrator.models.Deadline'
    ],

    config: {
        /**
         * @cfg
         * Delivery ``Ext.data.Model``.
         */
        assignmentgroup_id: undefined
    },

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
        this.deadlinestore = this.createDeadlineStore();
        this.loadAllDeadlines();
    },

    createDeadlineStore: function() {
        var deadlinestore = devilry.extjshelpers.RestFactory.createStore('administrator', 'Deadline', {
            filters: [{
                property: 'assignment_group',
                value: this.assignmentgroup_id
            }]
        });
        deadlinestore.proxy.setDevilryOrderby(['-deadline']);
        return deadlinestore;
    },

    loadAllDeadlines: function() {
        this.deadlinestore.loadAll({
            scope: this,
            callback: function(deadlineRecords) {
                Ext.each(deadlineRecords, function(deadlineRecord, index) {
                    //console.log(deadlineRecord);
                    var deliveries = deadlineRecord.deliveries();
                    deliveries.load(function(deliveryRecords) {
                        console.log(deadlineRecord.data.deadline, deliveryRecords.length);
                    });
                });
            }
        });
    }
});
