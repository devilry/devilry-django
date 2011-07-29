/** List deliveries grouped by deadline. */
Ext.define('devilry.extjshelpers.assignmentgroup.DeadlineListing', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.deadlinelisting',
    cls: 'widget-deadlinelisting',
    hideHeaders: true, // Hide column header
    rowTpl: Ext.create('Ext.XTemplate',
        '{number}. {time_of_delivery:date}',
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
         * Enable creation of new deadlines?
         */
        enableDeadlineCreation: false,

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
        if(this.enableDeadlineCreation) {
            this.addCreateNewDeadlineButton();
        }

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
                dock: 'top',
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
     * */
    addCreateNewDeadlineButton: function() {
        Ext.apply(this, {
            bbar: ['->', {
                xtype: 'button',
                text: 'Create new deadline',
                iconCls: 'icon-add-32',
                scale: 'large',
                listeners: {
                    click: function ()
                    {
                        console.log('TODO');
                    }
                }
            }]
        });
    },

    /**
     * @private
     * Reload all deadlines on this assignmentgroup.
     * */
    reload: function() {
        this.loadDeadlines(this.assignmentgroup_recordcontainer.record.data.id);
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
    loadDeadlines: function(assignmentgroupid) {
        this.store.proxy.extraParams.filters = Ext.JSON.encode([{
            field: 'deadline__assignment_group',
            comp: 'exact',
            value: assignmentgroupid
        }]);
        this.store.load();
    }
});
