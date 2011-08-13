/** List deliveries on a single group, grouped by deadline. */
Ext.define('devilry.extjshelpers.assignmentgroup.DeliveriesOnSingleGroupListing', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.deliveriesonsinglegrouplisting',
    cls: 'widget-deliveriesonsinglegrouplisting',
    requires: [
        'devilry.extjshelpers.RestfulSimplifiedEditWindowBase',
        'devilry.extjshelpers.RestfulSimplifiedEditPanel'
    ],
    hideHeaders: true, // Hide column header
    rowTpl: Ext.create('Ext.XTemplate',
        'Delivery number {number}, ',
        'delivered <span class="time_of_delivery">{time_of_delivery:date}</span>',
        '<tpl if="time_of_delivery &gt; deadline__deadline">',
        '   <span class="after-deadline">(After deadline)</span>',
        '</tpl>'
    ),

    config: {
        /**
         * @cfg
         * Delivery ``Ext.data.Model``.
         */
        deliverymodel: undefined,

        /**
         * @cfg
         * A {@link devilry.extjshelpers.SingleRecordContainer} for Delivery.
         * The record is changed when a user selects a delivery.
         */
        delivery_recordcontainer: undefined,

        /**
         * @cfg
         * A {@link devilry.extjshelpers.SingleRecordContainer} for AssignmentGroup.
         */
        assignmentgroup_recordcontainer: undefined
    },

    constructor: function(config) {
        this.callParent([config]);
        this.initConfig(config);
    },

    initComponent: function() {
        var groupingFeature = Ext.create('Ext.grid.feature.Grouping', {
            enableGroupingMenu: false,
            groupHeaderTpl: 'Deadline: {name:date}' // {name} is the current data from the groupField for some reason
        });

        this.store = this.createDeliveryStore();
        var me = this;
        Ext.apply(this, {
            features: [groupingFeature],
            columns: [{
                header: 'Data',
                dataIndex: 'id',
                flex: 1,
                tdCls: 'selectable-gridcell',
                renderer: function(value, metaData, deliveryrecord) {
                    //console.log(deliveryrecord.data);
                    return this.rowTpl.apply(deliveryrecord.data);
                }
            }],
            listeners: {
                scope: this,
                itemmouseup: this.onSelectDelivery
            },
            dockedItems: [{
                xtype: 'pagingtoolbar',
                store: this.store,
                dock: 'bottom',
                displayInfo: false
            }]
        });

        this.callParent(arguments);
        if(this.assignmentgroup_recordcontainer.record) {
            this.reload();
        }
        this.assignmentgroup_recordcontainer.addListener('setRecord', this.reload, this);
    },

    /**
     * @private
     * */
    createDeliveryStore: function() {
        var deliverystore = Ext.create('Ext.data.Store', {
            model: this.deliverymodel,
            remoteFilter: true,
            remoteSort: true,
            autoSync: true,
            groupField: 'deadline__deadline'
        });

        deliverystore.proxy.extraParams.orderby = Ext.JSON.encode(['-deadline__deadline', '-number']);
        return deliverystore;
    },

    /**
     * @private
     * Reload all deliveries on this assignmentgroup.
     * */
    reload: function() {
        this.loadDeliveries(this.assignmentgroup_recordcontainer.record.data.id);
    },

    /**
     * @private
     */
    onSelectDelivery: function(grid, deliveryRecord) {
        this.delivery_recordcontainer.setRecord(deliveryRecord);
        this.up('window').close();
    },

    /**
     * @private
     */
    loadDeliveries: function(assignmentgroupid) {
        this.store.proxy.extraParams.filters = Ext.JSON.encode([{
            field: 'deadline__assignment_group',
            comp: 'exact',
            value: assignmentgroupid
        }]);
        //this.store.load({
            //scope: this,
            //callback: function(records) {
                //console.log(records[0].data);
            //}
        //});
        this.store.load();
    }
});
