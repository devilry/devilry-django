
/** Panel to show Delivery info, such as:
 *
 *  - Files
 *  - Time of delivery
 *
 * @xtype deliveryinfo
 */
Ext.define('devilry.extjshelpers.DeliveryInfo', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.deliveryinfo',
    title: 'Delivery',
    cls: 'widget-deliveryinfo',
    html: '',
    tpl: Ext.create('Ext.XTemplate',
        '<dl>',
        '   <dt>Files</dt>',
        '   <tpl if="filemetas.length == 0">',
        '       <dd><em>No files delivered</em></dd>',
        '   </tpl>',
        '   <tpl if="filemetas.length &gt; 0">',
        '       <dd><ul><tpl for="filemetas">',
        '           <li>{data.filename}</li>',
        '       </tpl></ul></dd>',
        '   </tpl>',
        '   <tpl if="filemetas.errors">',
        '       <dd><span class="error">Error while loading files</span></dd>',
        '   </tpl>',
        '   <tpl if="!filemetas">',
        '       <dd><em>loading...</em></dd>',
        '   </tpl>',
        '   <dt>Time of delivery</dt>',
        '   <dd>{delivery.time_of_delivery:date}</dd>',
        '</dl>'
    ),

    config: {
        /**
         * @cfg
         * RestfulSimplifiedFileMeta store. __Required__.
         */
        filemetastore: undefined
    },

    initComponent: function() {
        if(this.delivery) {
            this.setDelivery(this.delivery);
        }
        this.callParent(arguments);
    },

    loadFileMetas: function(delivery) {
        var me = this;
        var store = this.filemetastore;
        store.proxy.extraParams.filters = Ext.JSON.encode([
            {field: 'delivery', comp:'exact', value: delivery.id}
        ]);
        store.load(function(filemetarecords, operation, success) {
            if(success) {
                me.createBody(delivery, filemetarecords);
            } else {
                me.createBody(delivery, {errors: true});
            }
        });
    },

    createBody: function(delivery, filemetas) {
        var html = this.tpl.apply({
            delivery: delivery,
            filemetas: filemetas
        });
        this.update(html);
    },

    setDelivery: function(delivery) {
        this.createBody(delivery, false);
        this.loadFileMetas(delivery);
    }
});
