
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
        'devilry.extjshelpers.assignmentgroup.StaticFeedbackEditableInfo',
        'devilry.extjshelpers.assignmentgroup.StaticFeedbackInfo',
        'devilry.extjshelpers.assignmentgroup.FileMetaBrowserPanel'
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
        'Time of delivery: <em>{time_of_delivery:date}</em>'
    ),

    initComponent: function() {
        var clsname = this.canExamine? 'StaticFeedbackEditableInfo': 'StaticFeedbackInfo';
        this.feedbackInfo = Ext.create('devilry.extjshelpers.assignmentgroup.' + clsname, {
            deliveryid: this.delivery.id,
            staticfeedbackstore: this.staticfeedbackstore,
            assignmentid: this.assignmentid
        });

        var me = this;
        Ext.apply(this, {
            items: [this.feedbackInfo],
            tbar: [{
                xtype: 'button',
                text: 'Browse files',
                listeners: {
                    scope: me,
                    click: me.showFileMetaBrowserWindow
                }
            }, '->', this.tpl.apply(this.delivery)]
        });
        this.callParent(arguments);
    },

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
                deliveryid: this.delivery.id
            }]
        }).show();

    }
});
