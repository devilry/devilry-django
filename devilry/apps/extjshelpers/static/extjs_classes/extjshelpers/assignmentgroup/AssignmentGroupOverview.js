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
        'devilry.extjshelpers.SingleRecordContainer'
    ],

    //title: 'Assignment group',

    config: {
        /**
         * @cfg
        * ID of the div to render title to. Defaults to 'content-heading'.
        */
        renderTitleTo: 'content-heading',

        /*Assignment group*
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
    createLayout: function() {
        Ext.apply(this, {
            border: false,
            items: [{
                xtype: 'assignmentgroupinfo',
                assignmentgroup_recordcontainer: this.assignmentgroup_recordcontainer,
                delivery_recordcontainer: this.delivery_recordcontainer,
                assignmentgroupstore: this.assignmentgroupstore,
                deliverymodel: this.deliverymodel,
                deadlinemodel: this.deadlinemodel,
                canExamine: this.canExamine
            }, {
                xtype: 'deliveryinfo',
                title: 'Delivery',
                filemetastore: this.filemetastore,
                delivery_recordcontainer: this.delivery_recordcontainer,
                deliverymodel: this.deliverymodel,
                assignmentgroup_recordcontainer: this.assignmentgroup_recordcontainer
            }, {
                xtype: this.canExamine? 'staticfeedbackeditor': 'staticfeedbackinfo',
                title: 'Feedback',
                staticfeedbackstore: this.staticfeedbackstore,
                delivery_recordcontainer: this.delivery_recordcontainer,
                isAdministrator: this.isAdministrator, // Only required by staticfeedbackeditor
                assignmentgroup_recordcontainer: this.assignmentgroup_recordcontainer, // Only required by staticfeedbackeditor
                deadlinemodel: this.deadlinemodel, // Only required by staticfeedbackeditor
                assignmentgroupmodel: this.assignmentgroupmodel, // Only required by staticfeedbackeditor
                gradeeditor_config_recordcontainer: this.gradeeditor_config_recordcontainer // Only required by staticfeedbackeditor
            }]
        });
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
