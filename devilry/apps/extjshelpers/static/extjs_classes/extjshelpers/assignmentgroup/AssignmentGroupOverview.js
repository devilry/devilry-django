/**
 *
 * Requires the following icnlude in the django template:
 *
 *     {% include "extjshelpers/AssignmentGroupOverviewExtjsClasses.django.html" %}
 */
Ext.define('devilry.extjshelpers.assignmentgroup.AssignmentGroupOverview', {
    extend: 'Ext.container.Container',
    alias: 'widget.assignmentgroupoverview',
    cls: 'widget-assignmentgroupoverview',
    requires: [
        'devilry.extjshelpers.assignmentgroup.DeliveryInfo',
        'devilry.extjshelpers.assignmentgroup.AssignmentGroupInfo',
        'devilry.extjshelpers.assignmentgroup.StaticFeedbackInfo',
        'devilry.extjshelpers.assignmentgroup.StaticFeedbackEditor',
        'devilry.extjshelpers.assignmentgroup.AssignmentGroupTitle',
        'devilry.extjshelpers.assignmentgroup.AssignmentGroupTodoListWindow',
        'devilry.extjshelpers.assignmentgroup.DeliveriesGroupedByDeadline',
        'devilry.extjshelpers.assignmentgroup.IsOpen',
        'devilry.extjshelpers.SingleRecordContainer'
    ],

    //title: 'Assignment group',

    config: {
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
        this.loadAssignmentgroupRecord(); // NOTE: Must come after createLayout() because components listen for the setRecord event
        this.selectDeliveryIfInQueryString();
    },

    /**
     * @private
     */
    createAttributes: function() {
        this.assignmentgroup_recordcontainer = Ext.create('devilry.extjshelpers.SingleRecordContainer');
        this.delivery_recordcontainer = Ext.create('devilry.extjshelpers.SingleRecordContainer');
        this.gradeeditor_config_recordcontainer = Ext.create('devilry.extjshelpers.SingleRecordContainer');

        this.role = !this.canExamine? 'student': this.isAdministrator? 'administrator': 'examiner';
        this.assignmentgroupmodel = Ext.ModelManager.getModel(this.getSimplifiedClassName('SimplifiedAssignmentGroup'));
        this.deliverymodel = Ext.ModelManager.getModel(this.getSimplifiedClassName('SimplifiedDelivery'));
        this.filemetastore = Ext.data.StoreManager.lookup(this.getSimplifiedClassName('SimplifiedFileMetaStore'));
        this.staticfeedbackstore = Ext.data.StoreManager.lookup(this.getSimplifiedClassName('SimplifiedStaticFeedbackStore'));
        this.deadlinemodel = Ext.ModelManager.getModel(this.getSimplifiedClassName('SimplifiedDeadline'));

        if(this.canExamine) {
            this.gradeeditor_config_model = Ext.ModelManager.getModel(Ext.String.format(
                'devilry.apps.gradeeditors.simplified.{0}.SimplifiedConfig',
                this.role
            ));

            this.assignmentgroupstore = Ext.data.StoreManager.lookup(this.getSimplifiedClassName('SimplifiedAssignmentGroupStore'));
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
    showFeedbackPanel: function() {
        this.feedbackPanel.show();
    },

    /**
     * @private
     */
    createLayout: function() {
        this.feedbackPanel = Ext.widget(this.canExamine? 'staticfeedbackeditor': 'staticfeedbackinfo', {
            title: 'Feedback',
            staticfeedbackstore: this.staticfeedbackstore,
            //hidden: true,
            region: 'center',
            width: 400,
            delivery_recordcontainer: this.delivery_recordcontainer,
            isAdministrator: this.isAdministrator, // Only required by staticfeedbackeditor
            assignmentgroup_recordcontainer: this.assignmentgroup_recordcontainer, // Only required by staticfeedbackeditor
            deadlinemodel: this.deadlinemodel, // Only required by staticfeedbackeditor
            assignmentgroupmodel: this.assignmentgroupmodel, // Only required by staticfeedbackeditor
            gradeeditor_config_recordcontainer: this.gradeeditor_config_recordcontainer // Only required by staticfeedbackeditor
        });
        if(this.delivery_recordcontainer.record) {
            this.showFeedbackPanel();
        } else {
            this.delivery_recordcontainer.addListener('setRecord', this.showFeedbackPanel, this);
        }

        Ext.apply(this, {
            layout: {
                type: 'vbox',
                align: 'stretch'
            },
            items: [{
                xtype: 'assignmentgrouptitle',
                singlerecordontainer: this.assignmentgroup_recordcontainer
            }, {
                xtype: 'container',
                layout: 'border',
                style: 'background-color: transparent',
                flex: 1,
                border: false,
                items: [{
                    xtype: 'container',
                    region: 'west',
                    margin: {right: 10},
                    width: 250,
                    layout: {
                        type: 'vbox',
                        align: 'stretch'
                    },
                    items: [{
                        xtype: 'container',
                        //title: 'Actions',
                        layout: {
                            type: 'hbox'
                        },
                        items: [{
                            xtype: 'assignmentgroup_isopen',
                            assignmentgroup_recordcontainer: this.assignmentgroup_recordcontainer,
                            canExamine: this.canExamine
                        }, {xtype: 'box', width: 10}, {
                            xtype: 'button',
                            hidden: !this.canExamine,
                            text: 'To-do',
                            scale: 'large',
                            listeners: {
                                scope: this,
                                click: function() {
                                    Ext.create('devilry.extjshelpers.assignmentgroup.AssignmentGroupTodoListWindow', {
                                        assignmentgroupstore: this.assignmentgroupstore,
                                        assignmentgroup_recordcontainer: this.assignmentgroup_recordcontainer
                                    }).show();
                                }
                            }
                        }]
                    }, {
                        xtype: 'deliveriesgroupedbydeadline',
                        margin: {top: 10},
                        assignmentgroup_recordcontainer: this.assignmentgroup_recordcontainer,
                        delivery_recordcontainer: this.delivery_recordcontainer,
                        flex: 1
                    //}, {
                        //xtype: 'assignmentgroupinfo',
                        //assignmentgroup_recordcontainer: this.assignmentgroup_recordcontainer,
                        //delivery_recordcontainer: this.delivery_recordcontainer,
                        //assignmentgroupstore: this.assignmentgroupstore,
                        //deliverymodel: this.deliverymodel,
                        //deadlinemodel: this.deadlinemodel,
                        //canExamine: this.canExamine
                    //}, {
                        //xtype: 'deliveryinfo',
                        //title: 'Delivery',
                        //filemetastore: this.filemetastore,
                        //delivery_recordcontainer: this.delivery_recordcontainer,
                        //deliverymodel: this.deliverymodel,
                        //assignmentgroup_recordcontainer: this.assignmentgroup_recordcontainer,
                        //listeners: {
                            //scope: this,
                            //deliveriesLoaded: this.onDeliveriesLoaded
                        //}
                    }]
                }, this.feedbackPanel]
            }]
        });
    },

    /** 
     * @private
     */
    onDeliveriesLoaded: function(deliverystore) {
        //var assignmentgroupdetails = this.down('assignmentgroupdetails');
        //assignmentgroupdetails.extradata.numDeliveries = deliverystore.totalCount;
        //assignmentgroupdetails.updateBody();
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
            this.down('deliveryinfo').onOtherDeliveries();
        }
    }
});
