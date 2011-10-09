Ext.define('devilry.extjshelpers.assignmentgroup.DeliveriesOnSingleGroupLoader', {
    requires: [
        'devilry.extjshelpers.RestFactory'
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
        //this.deliverystore = this.createDeliveryStore();
        //this.loadAllDeliveries();
    },

    createDeliveryStore: function() {
        var deliverystore = devilry.extjshelpers.RestFactory.createStore('administrator', 'Delivery');
        deliverystore.proxy.setDevilryFilters([{
            field: 'deadline__assignment_group',
            comp: 'exact',
            value: this.assignmentgroup_id
        }]);
        deliverystore.proxy.setDevilryOrderby(['-deadline__deadline', '-number']);
        return deliverystore;
    },
    loadAllDeliveries: function() {
        this.deliverystore.loadAll({
            scope: this,
            callback: function(records) {
                console.log(records);
            }
        });
    },

    createDeadlineStore: function() {
        var deadlinestore = devilry.extjshelpers.RestFactory.createStore('administrator', 'Deadline');
        //deadlinestore.proxy.setDevilryFilters([{
            //field: 'assignment_group',
            //comp: 'exact',
            //value: this.assignmentgroup_id
        //}]);
        deadlinestore.proxy.setDevilryOrderby(['-deadline']);
        return deadlinestore;
    },

    loadAllDeadlines: function() {
        this.deadlinestore.loadAll({
            scope: this,
            callback: function(records) {
                Ext.each(records, function(record, index) {
                    console.log(record.data.deadline);
                    record.deliveries().load();
                });
            }
        });
    }
});
