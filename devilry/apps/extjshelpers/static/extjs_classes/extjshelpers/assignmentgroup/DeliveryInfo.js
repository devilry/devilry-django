
/** Panel to show Delivery info, such as:
 *
 *  - Files
 *  - Time of delivery
 *
 * @xtype deliveryinfo
 */
Ext.define('devilry.extjshelpers.assignmentgroup.DeliveryInfo', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.deliveryinfo',
    title: 'Delivery',
    cls: 'widget-deliveryinfo',
    html: '',
    requires: [
        'devilry.extjshelpers.assignmentgroup.StaticFeedbackEditableInfo'
    ],

    config: {
        /**
         * @cfg {Object} A delivery object, such as ``data`` attribute of a
         * record loaded from a Delivery store or model.
         */
        delivery: undefined,


        /**
        * @cfg
        * Assignment id. (Required).
        */
        assignmentid: undefined,

        /**
         * @cfg {Ext.data.Store} FileMeta store. (Required).
         * _Note_ that ``filemetastore.proxy.extraParams`` is changed by this
         * class.
         */
        filemetastore: undefined
    },

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

    initComponent: function() {
        this.deliveryInfo = Ext.create('Ext.Component');

        //this.feedbackInfo = Ext.create('devilry.extjshelpers.assignmentgroup.StaticFeedbackInfo', {
        this.feedbackInfo = Ext.create('devilry.extjshelpers.assignmentgroup.StaticFeedbackEditableInfo', {
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
        this.filemetastore.proxy.extraParams.filters = Ext.JSON.encode([
            {field: 'delivery', comp:'exact', value: this.delivery.id}
        ]);
        this.filemetastore.load(function(filemetarecords, operation, success) {
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
