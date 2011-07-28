/**
 *
 * Requires the following definitions in the django template:
 *
 *     {{ restfulapi.RestfulSimplifiedAssignmentGroup|extjs_model:"subject,period,assignment,users" }};
 *    
 *     {{ restfulapi.RestfulSimplifiedDelivery|extjs_model:"deadline,assignment_group" }};
 *     {{ restfulapi.RestfulSimplifiedDelivery|extjs_store }};
 *    
 *     {{ restfulapi.RestfulSimplifiedStaticFeedback|extjs_model }};
 *     {{ restfulapi.RestfulSimplifiedStaticFeedback|extjs_store }};
 *    
 *     {{ restfulapi.RestfulSimplifiedFileMeta|extjs_model }};
 *     {{ restfulapi.RestfulSimplifiedFileMeta|extjs_store }};
 *    
 *     {# These are used by the grade editor and only required is canExamine is true #}
 *     {{ gradeeditors.RestfulSimplifiedConfig|extjs_model }};
 *     {{ gradeeditors.RestfulSimplifiedFeedbackDraft|extjs_model }};
 *     {{ gradeeditors.RestfulSimplifiedFeedbackDraft|extjs_store }};
 *
 * The ones from ``restfulapi`` are for core classes, while the ones from
 * ``gradeeditors`` is from ``devilry.apps.gradeeditors``. You can dump this
 * code into the django template using:
 *
 *     {% include "extjshelpers/AssignmentGroupOverviewExtjsClasses.django.html" %}
 */
Ext.define('devilry.extjshelpers.assignmentgroup.AssignmentGroupOverview', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.assignmentgroupoverview',
    cls: 'widget-assignmentgroupoverview',
    requires: [
        'devilry.extjshelpers.assignmentgroup.DeliveryInfo',
        'devilry.extjshelpers.assignmentgroup.AssignmentGroupDetailsPanel',
        'devilry.extjshelpers.assignmentgroup.DeadlineListing',
        'devilry.extjshelpers.assignmentgroup.StaticFeedbackInfo',
        'devilry.extjshelpers.assignmentgroup.StaticFeedbackEditor',
        'devilry.extjshelpers.assignmentgroup.AssignmentGroupTitle',
        'devilry.extjshelpers.SingleRecordContainer'
    ],

    headingTpl: Ext.create('Ext.XTemplate',
        '<div class="treeheader">',
        '   <div class="level1">{parentnode__parentnode__parentnode__long_name}</div>',
        '   <div class="level2">{parentnode__parentnode__long_name}</div>',
        '   <div class="level3">{parentnode__long_name}</div>',
        '<div>'
    ),

    config: {
        /**
         * @cfg
        * ID of the div to render title to. Defaults to 'content-heading'.
        */
        renderTitleTo: 'content-heading',

        /**
         * @cfg
        * ID of the div to render the body to. Defaults to 'content-main'.
        */
        renderTo: 'content-main',

        /**
         * @cfg
         * Enable creation of new feedbacks? Defaults to ``false``.
         * See: {@link devilry.extjshelpers.assignmentgroup.DeliveryInfo#canExamine}.
         *
         * When this is ``true``, the authenticated user still needs to have
         * permission to POST new feedbacks for the view to work.
         */
        canExamine: false,

        /**
         * @cfg
         * AssignmentGroup ID.
         */
        assignmentgroupid: undefined,

        /**
         * @cfg
         * Use the administrator RESTful interface to store drafts? If this is
         * ``false``, we use the examiner RESTful interface.
         */
        isAdministrator: false
    },

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },


    initComponent: function() {
        this.createAttributes();
        this.createLayout();
        this.callParent(arguments);
        this.loadAssignmentgroupRecord();
        this.selectDeliveryIfInQueryString();
    },

    /**
     * @private
     */
    createAttributes: function() {
        this.assignmentgroup_recordcontainer = Ext.create('devilry.extjshelpers.SingleRecordContainer');
        this.delivery_recordcontainer = Ext.create('devilry.extjshelpers.SingleRecordContainer');
        this.gradeeditor_config_recordcontainer = Ext.create('devilry.extjshelpers.SingleRecordContainer');

        Ext.create('devilry.extjshelpers.assignmentgroup.AssignmentGroupTitle', {
            renderTo: this.renderTitleTo,
            singlerecordontainer: this.assignmentgroup_recordcontainer
        });

        this.role = !this.canExamine? 'student': this.isAdministrator? 'administrator': 'examiner';
        this.assignmentgroupmodel = Ext.ModelManager.getModel(this.getSimplifiedClassName('SimplifiedAssignmentGroup'));
        this.deliverymodel = Ext.ModelManager.getModel(this.getSimplifiedClassName('SimplifiedDelivery'));
        this.filemetastore = Ext.data.StoreManager.lookup(this.getSimplifiedClassName('SimplifiedFileMetaStore'));
        this.staticfeedbackstore = Ext.data.StoreManager.lookup(this.getSimplifiedClassName('SimplifiedStaticFeedbackStore'));

        if(this.canExamine) {
            this.gradeeditor_config_model = Ext.ModelManager.getModel(Ext.String.format(
                'devilry.apps.gradeeditors.simplified.{0}.SimplifiedConfig',
                this.role
            ));
        }
    },

    /**
     * @private
     */
    loadAssignmentgroupRecord: function() {
        this.assignmentgroupmodel.load(this.assignmentgroupid, {
            scope: this,
            success: function(record) {
                this.assignmentgroup_recordcontainer.setRecord(record);
                this.loadGradeEditorConfigModel();
            },
            failure: function() {
                // TODO: Handle errors
            }
        });
    },

    /**
     * @private
     */
    loadGradeEditorConfigModel: function() {
        if(this.canExamine) {
            this.gradeeditor_config_model.load(this.assignmentgroup_recordcontainer.record.data.parentnode, {
                scope: this,
                success: function(record) {
                    this.gradeeditor_config_recordcontainer.setRecord(record);
                },
                failure: function() {
                    // TODO: Handle errors
                }
            });
        }
    },

    /**
     * @private
     */
    getSimplifiedClassName: function(name) {
        var classname = Ext.String.format(
            'devilry.apps.{0}.simplified.{1}',
            this.role, name
        );
        return classname;
    },

    /**
     * @private
     */
    createLayout: function() {
        this.onOtherDeliveriesBtn = Ext.ComponentManager.create({
            xtype: 'button',
            menu: [], // To get an arrow
            text: 'Other deliveries/deadlines',
            scale: 'large',
            enableToggle: true,
            listeners: {
                scope: this,
                click: this.onOtherDeliveries
            }
        });
        Ext.apply(this, {
            //width: 1000,
            //height: 800,
            tbar: [this.onOtherDeliveriesBtn, '->', {
                xtype: 'deliveryinfo',
                delivery_recordcontainer: this.delivery_recordcontainer,
                filemetastore: this.filemetastore
            }],
            items: [{
                items: [{
                    xtype: this.canExamine? 'staticfeedbackeditor': 'staticfeedbackinfo',
                    staticfeedbackstore: this.staticfeedbackstore,
                    delivery_recordcontainer: this.delivery_recordcontainer,
                    isAdministrator: this.isAdministrator, // Only required by staticfeedbackeditor
                    gradeeditor_config_recordcontainer: this.gradeeditor_config_recordcontainer // Only required by staticfeedbackeditor
                }]
            }]
        });
    },

    /**
     * @private
     */
    onOtherDeliveries: function(button) {
        if(!this.deliveriesWindow) {
            this.deliveriesWindow = Ext.create('Ext.window.Window', {
                title: 'Deliveries grouped by deadline',
                height: 500,
                width: 400,
                modal: true,
                layout: 'fit',
                closeAction: 'hide',
                items: {
                    xtype: 'deadlinelisting',
                    assignmentgroup_recordcontainer: this.assignmentgroup_recordcontainer,
                    delivery_recordcontainer: this.delivery_recordcontainer,
                    deliverymodel: this.deliverymodel,
                    enableDeadlineCreation: this.canExamine
                },
                listeners: {
                    scope: this,
                    close: function() {
                        this.onOtherDeliveriesBtn.toggle(false);
                    }
                }
            });
        }
        this.deliveriesWindow.show();
        if(button) {
            this.deliveriesWindow.alignTo(button, 'bl', [0, 0]);
        }
    },

    /**
     * @private
     */
    selectDeliveryIfInQueryString: function() {
        var query = Ext.Object.fromQueryString(window.location.search);
        if(query.deliveryid) {
            var deliveryid = parseInt(query.deliveryid);
            this.deliverymodel.load(deliveryid, {
                scope: this,
                success: function(record) {
                    if(this.assignmentgroupid == record.data.deadline__assignment_group) {
                        this.delivery_recordcontainer.setRecord(record);
                    } else {
                        throw Ext.String.format(
                            'Delivery {0} is not in AssignmentGroup {1}',
                            deliveryid,
                            this.assignmentgroupid
                        );
                    }
                },
                failure: function() {
                    // TODO: Handle errors
                }
            });
        } else {
            this.onOtherDeliveries();
        }
    }
});
