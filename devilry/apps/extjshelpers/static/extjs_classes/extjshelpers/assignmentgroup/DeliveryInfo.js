
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
        delivery_recordcontainer: undefined
    },

    toolbarTpl: Ext.create('Ext.XTemplate',
        'Time of delivery: <em>{time_of_delivery:date}</em>'
    ),

    initComponent: function() {
        this.callParent(arguments);
        if(this.delivery_recordcontainer.record) {
            this.onLoadDelivery();
        }
        this.delivery_recordcontainer.addListener('setRecord', this.onLoadDelivery, this);
    },

    /**
     * @private
     */
    onLoadDelivery: function() {
        if(this.toolbar) {
            this.removeDocked(this.toolbar);
        }
        this.toolbar = Ext.ComponentManager.create({
            xtype: 'toolbar',
            dock: 'top',
            items: [{
                xtype: 'button',
                text: 'Browse files',
                listeners: {
                    scope: this,
                    click: this.showFileMetaBrowserWindow
                }
            }, '->', this.toolbarTpl.apply(this.delivery_recordcontainer.record.data)]
        });
        this.addDocked(this.toolbar);
    },

    /**
     * @private
     */
    showFileMetaBrowserWindow: function() {
        Ext.create('Ext.window.Window', {
            title: 'Files',
            height: 400,
            width: 600,
            layout: 'fit',
            items: [{
                xtype: 'filemetabrowserpanel',
                border: false,
                filemetastore: this.filemetastore,
                deliveryid: this.delivery_recordcontainer.record.data.id
            }]
        }).show();
    }
});
