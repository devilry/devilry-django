
/**
 * Panel to show Delivery info.
 */
Ext.define('devilry.extjshelpers.assignmentgroup.DeliveryInfo', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.deliveryinfo',
    cls: 'widget-deliveryinfo',
    html: '',
    requires: [
        'devilry.extjshelpers.assignmentgroup.FileMetaBrowserPanel'
    ],

    //width: 500,
    //style: {border: 'none'},

    config: {
        /**
         * @cfg
         * FileMeta ``Ext.data.Store``. (Required).
         * _Note_ that ``filemetastore.proxy.extraParams`` is changed by this
         * class.
         */
        filemetastore: undefined,

        /**
         * @cfg
         * A {@link devilry.extjshelpers.SingleRecordContainer} for Delivery.
         */
        delivery_recordcontainer: undefined,

        /**
         * @cfg
         * Delivery ``Ext.data.Model``.
         */
        deliverymodel: undefined,

        /**
         * @cfg
         * A {@link devilry.extjshelpers.SingleRecordContainer} for AssignmentGroup.
         */
        assignmentgroup_recordcontainer: undefined
    },

    tpl: Ext.create('Ext.XTemplate',
        '<tpl if="time_of_delivery">', // If time_of_delivery is false, the record is not loaded yet
        '    <tpl if="time_of_delivery &gt; deadline__deadline">',
        '        <section class="warning-small">',
        '           <h1>After deadline</h1>',
        '           <p>This delivery was made <strong>after</strong> the deadline (<em>{deadline__deadline:date}</em>).</p>',
        '        </section>',
        '    </tpl>',
        '    <tpl if="!islatestDelivery">',
        '        <section class="warning-small">',
        '           <h1>Not the latest delivery</h1>',
        '           <p>',
        '               The group has made one or more deliveries after the one you are currently viewing. <em>Normally</em> the latest delivery is corrected.',
        '               <tpl if="time_of_delivery &gt; deadline__deadline">',
        '                   However since this delivery was made after the deadline, an earlier delivery may be corrected instead.',
        '               </tpl>',
        '               Choose <span class="menuref">Other deliveries</span> in the toolbar to view other deliveries.',
        '           </p>',
        '        </section>',
        '    </tpl>',
        '    <section class="info-small">',
        '       <h1>Delivery number {number}</h1>',
        '       <p>This delivery was made <em>{time_of_delivery:date}</em>. Choose <span class="menuref">Browse files</span> in the toolbar to download the delivered files.</p>',
        '    </section>',
        '</tpl>'
    ),

    initComponent: function() {
        this.toolbar = Ext.widget('toolbar', {
            xtype: 'toolbar',
            dock: 'top',
            items: []
        });
        
        Ext.apply(this, {
            hidden: true,
            dockedItems: [this.toolbar]
        });
        this.callParent(arguments);

        this.deliverystore = this.createDeliveryStore();

        if(this.assignmentgroup_recordcontainer.record) {
            this.loadDeliveryStore();
        }
        this.assignmentgroup_recordcontainer.addListener('setRecord', this.loadDeliveryStore, this);

        if(this.delivery_recordcontainer.record) {
            this.onLoadDelivery();
        }
        this.delivery_recordcontainer.addListener('setRecord', this.onLoadSomething, this);
    },

    /**
     * @private
     */
    onLoadSomething: function() {
        if(this.delivery_recordcontainer.record && this.deliverystoreLoaded) {
            this.onLoadingComplete();
        }
    },

    /**
     * @private
     * Reload all deliveries on this assignmentgroup.
     * */
    loadDeliveryStore: function() {
        //this.deliverystore.pageSize = 3;
        this.deliverystore.proxy.extraParams.filters = Ext.JSON.encode([{
            field: 'deadline__assignment_group',
            comp: 'exact',
            value: this.assignmentgroup_recordcontainer.record.data.id
        }]);
        this.deliverystore.load({
            scope: this,
            callback: function(records, op, success) {
                if(success) {
                    this.deliverystoreLoaded = true;
                    this.fireEvent('deliveriesLoaded', this.deliverystore);
                    this.onLoadSomething(records);
                } else {
                    throw "Failed to load delivery store.";
                }
            }
        });
    },

    /**
     * @private
     */
    onLoadingComplete: function() {
        var delivery = this.delivery_recordcontainer.record.data;
        var islatestDelivery = this.deliverystore.currentPage == 1 && this.deliverystore.data.items[0].data.id == delivery.id;

        this.show();
        this.toolbar.removeAll();

        var data = {
            islatestDelivery: islatestDelivery
        };
        Ext.apply(data, delivery);
        this.update(data);

        this.toolbar.add({
            xtype: 'button',
            text: 'Browse files',
            id: 'tooltip-browse-files',
            scale: 'large',
            menu: [], // To get an arrow
            enableToggle: true,
            listeners: {
                scope: this,
                click: this.showFileMetaBrowserWindow,
                render: function() {
                    Ext.create('devilry.extjshelpers.tooltips.assignmentgroup.BrowseFiles', {});
                }
            }
        });

        this.toolbar.add({
            xtype: 'button',
            menu: [], // To get an arrow
            id: 'tooltip-other-deliveries',
            text: 'Other deliveries',
            scale: 'large',
            //enableToggle: true,
            listeners: {
                scope: this,
                click: this.onOtherDeliveries
            }
        });
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
     */
    onOtherDeliveries: function(button, notClosable) {
        var deliveriesWindow = Ext.create('Ext.window.Window', {
            title: 'Deliveries by this group',
            height: 500,
            width: 400,
            modal: true,
            layout: 'fit',
            closeAction: 'hide',
            //closable: button != undefined,
            items: {
                xtype: 'deliveriesonsinglegrouplisting',
                store: this.deliverystore,
                delivery_recordcontainer: this.delivery_recordcontainer
            }
        });
        deliveriesWindow.show();
        if(button) {
            deliveriesWindow.alignTo(button, 'bl', [0, 0]);
        }
    },

    /**
     * @private
     */
    showFileMetaBrowserWindow: function(button) {
        var fileBrowser = Ext.create('Ext.window.Window', {
            title: 'Files',
            height: 400,
            width: 500,
            modal: true,
            //animateTarget: button,
            layout: 'fit',
            items: [{
                xtype: 'filemetabrowserpanel',
                border: false,
                filemetastore: this.filemetastore,
                deliveryid: this.delivery_recordcontainer.record.data.id
            }],
            listeners: {
                scope: this,
                close: function() {
                    button.toggle(false);
                }
            }
        });
        fileBrowser.show();
        fileBrowser.alignTo(button, 'bl', [0, 0]);
    }
});
