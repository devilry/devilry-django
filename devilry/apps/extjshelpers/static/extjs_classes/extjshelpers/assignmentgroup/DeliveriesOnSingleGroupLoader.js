Ext.define('devilry.extjshelpers.assignmentgroup.DeliveriesOnSingleGroupLoader', {
    requires: [
        'devilry.extjshelpers.RestFactory'
    ],

    config: {
        /**
         * @cfg
         * Delivery ``Ext.data.Model``.
         */
        deliverymodel: undefined,
        assignmentgroup_recordcontainer: undefined
    },

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);

        if(this.assignmentgroup_recordcontainer.record) {
            this.onSetAssignmentGroupRecord();
        } else {
            this.assignmentgroup_recordcontainer.addListener('setRecord', this.onSetAssignmentGroupRecord, this);
        }
    },

    onSetAssignmentGroupRecord: function() {
        this.store = this.createDeliveryStore();
        this.loadAllDeliveries();
    },

    createDeliveryStore: function() {
        var deliverystore = devilry.extjshelpers.RestFactory.createStore('administrator', 'Delivery');
        deliverystore.proxy.setDevilryFilters([{
            field: 'deadline__assignment_group',
            comp: 'exact',
            value: this.assignmentgroup_recordcontainer.record.data.id
        }]);
        deliverystore.proxy.setDevilryOrderby(['-deadline__deadline', '-number']);
        return deliverystore;
    },

    loadAllDeliveries: function() {
        this.store.loadAll({
            scope: this,
            callback: function(records) {
                console.log(records);
            }
        });
    }
});
