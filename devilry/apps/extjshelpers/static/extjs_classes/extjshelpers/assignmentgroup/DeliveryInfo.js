
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
        delivery_recordcontainer: undefined
    },

    tpl: Ext.create('Ext.XTemplate',
        '<tpl if="time_of_delivery">', // If time_of_delivery is false, the record is not loaded yet
        '    <section class="info-small">',
        '       <h1>Delivery number {number}</h1>',
        '       <p>This delivery was made <em>{time_of_delivery:date}</em>. Choose <span class="menuref">Browse files</span> in the toolbar to download the delivered files.</p>',
        '    </section>',
        '    <tpl if="time_of_delivery &gt; deadline__deadline">',
        '        <section class="warning-small">',
        '           <h1>After deadline</h1>',
        '           <p>This delivery was made <strong>after</strong> the deadline (<em>{deadline__deadline:date}</em>).</p>',
        '        </section>',
        '    </tpl>',
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
        this.toolbar.removeAll();
        this.update(delivery);
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
