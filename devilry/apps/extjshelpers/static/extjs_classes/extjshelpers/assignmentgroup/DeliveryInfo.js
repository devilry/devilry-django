
/**
 * Panel to show Delivery info.
 * Uses {@link devilry.extjshelpers.assignmentgroup.StaticFeedbackInfo}
 * or {@link devilry.extjshelpers.assignmentgroup.StaticFeedbackEditableInfo}
 * to show and manage StaticFeedback (see {@link #canExamine})
 *
 *      -------------------------------------------
 *      | Info about the delivery                 |
 *      |                                         |
 *      |                                         |
 *      -------------------------------------------
 *      | StaticFeedbackInfo                      |
 *      | or                                      |
 *      | StaticFeedbackEditableInfo              |
 *      |                                         |
 *      |                                         |
 *      |                                         |
 *      |                                         |
 *      -------------------------------------------
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
         * @cfg
         * A delivery object, such as ``data`` attribute of a
         * record loaded from a Delivery store or model.
         */
        delivery: undefined,

        /**
         * @cfg
         * Enable creation of new feedbacks? Defaults to ``false``.
         *
         * If this is ``true``, 
         * {@link devilry.extjshelpers.assignmentgroup.StaticFeedbackEditableInfo}
         * is used instead of
         * {@link devilry.extjshelpers.assignmentgroup.StaticFeedbackInfo}.
         *
         * If this is ``true``, the ``assignmentid`` config is _required_.
         *
         * When this is ``true``, the authenticated user still needs to have
         * permission to POST new feedbacks for the view to work.
         */
        canExamine: false,

        /**
        * @cfg
        * Assignment id. Required for 
        * {@link devilry.extjshelpers.assignmentgroup.StaticFeedbackEditableInfo},
        * which is used if the ``canExamine`` config is ``true``.
        */
        assignmentid: undefined,

        /**
         * @cfg
         * FileMeta ``Ext.data.Store``. (Required).
         * _Note_ that ``filemetastore.proxy.extraParams`` is changed by this
         * class.
         */
        filemetastore: undefined,

        /**
         * @cfg
         * FileMeta ``Ext.data.Store``. (Required).
         * _Note_ that ``filemetastore.proxy.extraParams`` is changed by
         * {@link devilry.extjshelpers.assignmentgroup.StaticFeedbackInfo}.
         */
        staticfeedbackstore: undefined
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

        var clsname = this.canExamine? 'StaticFeedbackEditableInfo': 'StaticFeedbackInfo';
        this.feedbackInfo = Ext.create('devilry.extjshelpers.assignmentgroup.' + clsname, {
            deliveryid: this.delivery.id,
            staticfeedbackstore: this.staticfeedbackstore,
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
