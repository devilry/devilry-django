
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
    requires: [
        'devilry.extjshelpers.StaticFeedbackEditableInfo'
    ],
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
         */
        delivery: undefined,
        assignmentid: undefined
    },

    initComponent: function() {
        this.deliveryInfo = Ext.create('Ext.Component');

        //this.feedbackInfo = Ext.create('devilry.extjshelpers.StaticFeedbackInfo', {
        this.feedbackInfo = Ext.create('devilry.extjshelpers.StaticFeedbackEditableInfo', {
            deliveryid: this.delivery.id,
            assignmentid: this.assignmentid
        });


        Ext.apply(this, {
            items: [this.deliveryInfo, this.feedbackInfo]
        });
        this.createBody(false);
        this.loadFileMetas();
        this.callParent(arguments);
    },

    loadFileMetas: function() {
        var me = this;
        var filemetastoreid = 'devilry.apps.examiner.simplified.SimplifiedFileMetaStore';
        var store = Ext.data.StoreManager.lookup(filemetastoreid);
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
        this.deliveryInfo.update(html);
    }
});
