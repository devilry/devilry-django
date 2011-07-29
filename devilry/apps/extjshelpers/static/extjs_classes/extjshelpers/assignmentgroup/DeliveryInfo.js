
/**
 * Panel to show Delivery info.
 */
Ext.define('devilry.extjshelpers.assignmentgroup.DeliveryInfo', {
    extend: 'Ext.toolbar.Toolbar',
    alias: 'widget.deliveryinfo',
    cls: 'widget-deliveryinfo',
    html: '',
    requires: [
        'devilry.extjshelpers.assignmentgroup.FileMetaBrowserPanel'
    ],

    width: 500,
    style: {border: 'none'},

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

    timeOfDeliveryTpl: Ext.create('Ext.XTemplate',
        '<span class="time_of_delivery">',
        '   Time of delivery: <em>{time_of_delivery:date}</em>',
        '   <tpl if="time_of_delivery &gt; deadline__deadline">',
        '       <span class="after-deadline">(After deadline)</span>',
        '   </tpl>',
        '</span>'
    ),

    initComponent: function() {
        Ext.apply(this, {
            hidden: true,
        });
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
        var delivery = this.delivery_recordcontainer.record.data;
        this.show();
        this.removeAll();
        this.add('->');
        this.add(this.timeOfDeliveryTpl.apply(delivery));
        this.add('-');
        this.add({
            xtype: 'button',
            text: 'Browse files',
            id: 'tooltip-browse-files',
            scale: 'large',
            listeners: {
                scope: this,
                click: this.showFileMetaBrowserWindow
            }
        });
    },

    /**
     * @private
     */
    showFileMetaBrowserWindow: function(button) {
        Ext.create('Ext.window.Window', {
            title: 'Files',
            height: 400,
            width: 600,
            modal: true,
            animateTarget: button,
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
