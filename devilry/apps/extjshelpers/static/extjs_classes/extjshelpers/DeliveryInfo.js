
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
        filemetastore: undefined,

        /**
         * @cfg
         * Delivery object as returned from loading it by id as a model.
         */
        delivery: undefined
    },

    loadFileMetas: function() {
        var me = this;
        var store = this.filemetastore;
        store.proxy.extraParams.filters = Ext.JSON.encode([
            {field: 'delivery', comp:'exact', value: this.delivery.id}
        ]);
        store.load(function(filemetarecords, operation, success) {
            if(success) {
                me.createBody(filemetarecords);
            } else {
                me.createBody({errors: true});
            }
        });
    },

    createBody: function(filemetas) {
        var html = this.tpl.apply({
            delivery: this.delivery,
            filemetas: filemetas
        });
        this.update(html);
    },

    initComponent: function() {
        this.callParent(arguments);
        this.createBody(false);
        this.loadFileMetas();
    }
});
