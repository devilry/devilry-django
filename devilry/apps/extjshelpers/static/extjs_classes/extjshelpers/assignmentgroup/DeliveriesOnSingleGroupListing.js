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

    helptext: '<div class="section helpsection">' +
        '   <p>Select a delivery from the list of all deliveries made by this group. The deliveries are grouped by deadline.</p>' +
        '   <p>Deliveries are numbered by the order they are delivered. The first delivery has number <strong>1</strong>.</p>' +
        '   <p>Deliveries are made on a specific deadline. Students can deliver after the deadline, as long as the group is open. However when a delivery was made after the deadline, it is shown by a message after the time of delivery.</p>' +
        '</div>',

    config: {
        /**
         * @cfg
         * A {@link devilry.extjshelpers.SingleRecordContainer} for Delivery.
         * The record is changed when a user selects a delivery.
         */
        delivery_recordcontainer: undefined
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

        this.pagingtoolbar = Ext.widget('pagingtoolbar', {
            store: this.store,
            dock: 'bottom',
            displayInfo: false
        });

        var me = this;
        Ext.apply(this, {
            features: [groupingFeature],
            columns: [{
                header: 'Data',
                dataIndex: 'id',
                flex: 1,
                renderer: function(value, metaData, deliveryrecord) {
                    //console.log(deliveryrecord.data);
                    return this.rowTpl.apply(deliveryrecord.data);
                }
            }],
            listeners: {
                scope: this,
                itemmouseup: this.onSelectDelivery
            },
            dockedItems: [this.pagingtoolbar, {
                xtype: 'panel',
                html: this.helptext,
                dock: 'right',
                width: 300
            }]
        });

        this.store.addListener('load', this.onLoadStore, this);

        this.callParent(arguments);
    },

    /**
     * @private
     */
    onLoadStore: function() {
        if(this.store.totalCount == 0) {
            this.up('window').close();
        };
        //this.removeDocked(this.pagingtoolbar);
        //this.addDocked({
            //xtype: 'box',
            //dock: 'top',
            //padding: 10,
            //frame: true,
            //html: 'This group has no deliveries. Close this window and '
        //});
    },

    /**
     * @private
     */
    onSelectDelivery: function(grid, deliveryRecord) {
        this.delivery_recordcontainer.setRecord(deliveryRecord);
        this.up('window').close();
    },
});
