/**
 *
 * Requires the following icnlude in the django template:
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
        'devilry.extjshelpers.assignmentgroup.DeliveriesOnSingleGroupListing',
        'devilry.extjshelpers.assignmentgroup.DeadlinesOnSingleGroupListing',
        'devilry.extjshelpers.assignmentgroup.StaticFeedbackInfo',
        'devilry.extjshelpers.assignmentgroup.StaticFeedbackEditor',
        'devilry.extjshelpers.assignmentgroup.AssignmentGroupTitle',
        'devilry.extjshelpers.assignmentgroup.AssignmentGroupTodoList',
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

        if(this.canExamine) {
            this.gradeeditor_config_model = Ext.ModelManager.getModel(Ext.String.format(
                'devilry.apps.gradeeditors.simplified.{0}.SimplifiedConfig',
                this.role
            ));

            this.assignmentgroupstore = Ext.data.StoreManager.lookup(this.getSimplifiedClassName('SimplifiedAssignmentGroupStore'));
            this.deadlinemodel = Ext.ModelManager.getModel(this.getSimplifiedClassName('SimplifiedDeadline'));

            this.assignmentgroup_recordcontainer.addListener('setRecord', this.onSetAssignmentGroup, this);
        }

    },

    /**
     * @private
     */
    onSetAssignmentGroup: function() {
        this.closeopenbtn.setText(this.assignmentgroup_recordcontainer.record.data.is_open? 'Close group': 'Open group');
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
            id: 'tooltip-other-deliveries',
            text: 'Deliveries',
            scale: 'large',
            enableToggle: true,
            listeners: {
                scope: this,
                click: this.onOtherDeliveries
            }
        });

        var tbarItems = [{
            xtype: 'button',
            menu: [], // To get an arrow
            id: 'tooltip-deliveries',
            text: 'Deadlines',
            scale: 'large',
            enableToggle: true,
            listeners: {
                scope: this,
                click: this.onDeadlines
            }
        }, this.onOtherDeliveriesBtn];
        
        if(this.canExamine) {
            var onUncorrectedGroupsBtn = Ext.ComponentManager.create({
                xtype: 'button',
                menu: [], // To get an arrow
                id: 'tooltip-uncorrected-groups',
                text: 'To-do',
                scale: 'large',
                enableToggle: true,
                listeners: {
                    scope: this,
                    click: this.onUncorrectedGroups
                }
            });
            Ext.Array.insert(tbarItems, 0, [onUncorrectedGroupsBtn]);

            this.closeopenbtn = Ext.ComponentManager.create({
                xtype: 'button',
                menu: [], // To get an arrow
                text: '',
                scale: 'large',
                enableToggle: true,
                listeners: {
                    scope: this,
                    click: this.onCloseOrOpenGroup
                }
            });
            Ext.Array.insert(tbarItems, 3, [this.closeopenbtn]);
        }


        Ext.apply(this, {
            xtype: 'panel',
            frame: false,
            tbar: tbarItems,
            items: [{
                xtype: 'box',
                html: 'todo',
            }, {
                xtype: 'deliveryinfo',
                title: 'Delivery',
                delivery_recordcontainer: this.delivery_recordcontainer,
                frame: false,
                //border: false,
                filemetastore: this.filemetastore
            }, {
                xtype: this.canExamine? 'staticfeedbackeditor': 'staticfeedbackinfo',
                staticfeedbackstore: this.staticfeedbackstore,
                delivery_recordcontainer: this.delivery_recordcontainer,
                isAdministrator: this.isAdministrator, // Only required by staticfeedbackeditor
                gradeeditor_config_recordcontainer: this.gradeeditor_config_recordcontainer // Only required by staticfeedbackeditor
            }]
        });
    },


    /**
     * @private
     */
    onUncorrectedGroups: function(button) {
        var groupsWindow = Ext.create('Ext.window.Window', {
            title: 'To-do list (Open groups on this assignment)',
            height: 500,
            width: 400,
            modal: true,
            layout: 'fit',
            items: {
                xtype: 'assignmentgrouptodolist',
                assignmentgroup_recordcontainer: this.assignmentgroup_recordcontainer,
                store: this.assignmentgroupstore
            },
            listeners: {
                scope: this,
                close: function() {
                    button.toggle(false);
                }
            }
        });
        groupsWindow.show();
        groupsWindow.alignTo(button, 'bl', [0, 0]);
    },

    /**
     * @private
     */
    onOtherDeliveries: function(button) {
        if(!this.deliveriesWindow) {
            this.deliveriesWindow = Ext.create('Ext.window.Window', {
                title: 'Deliveries by this group',
                height: 500,
                width: 400,
                modal: true,
                layout: 'fit',
                closeAction: 'hide',
                items: {
                    xtype: 'deliveriesonsinglegrouplisting',
                    assignmentgroup_recordcontainer: this.assignmentgroup_recordcontainer,
                    delivery_recordcontainer: this.delivery_recordcontainer,
                    deliverymodel: this.deliverymodel,
                    deadlinemodel: this.deadlinemodel,
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
    onCloseOrOpenGroup: function(button) {
        if(this.assignmentgroup_recordcontainer.record.data.is_open) {
            this.onCloseGroup(button);
        } else {
            this.onOpenGroup(button);
        }
    },

    /**
     * @private
     */
    onOpenGroup: function(button) {
        var win = Ext.MessageBox.show({
            title: 'Are you sure you want to open this group?',
            msg: '<p>This will <strong>allow</strong> students to add more deliveries. ' +
                'Normally Devilry will close groups automatically when:</p>'+
                '<ul>' +
                '   <li>you have given a passing grade.</li>' +
                '   <li>students have failed to get a passing grade more than the configured maximum number of times.</li>' +
                '</ul>' +
                '<p>And you normally do not open it again unless you want students to add a new delivery.</p>',
            buttons: Ext.Msg.YESNO,
            scope: this,
            closable: false,
            fn: function(buttonId) {
                if(buttonId == 'yes') {
                    this.assignmentgroup_recordcontainer.record.data.is_open = true;
                    this.assignmentgroup_recordcontainer.record.save({
                        scope: this,
                        success: function(record) {
                            this.assignmentgroup_recordcontainer.fireSetRecordEvent();
                        },
                        failure: function() {
                            throw "Failed to open group."
                        }
                    });
                }
                button.toggle(false);
            }
        });
        win.alignTo(button, 'bl', [0, 0]);
    },

    /**
     * @private
     */
    onCloseGroup: function(button) {
        var win = Ext.MessageBox.show({
            title: 'Are you sure you want to close this group?',
            msg: '<p>This will <strong>prevent</strong> students from adding more deliveries. ' +
                'Normally Devilry will close groups automatically when:</p>'+
                '<ul>' +
                '   <li>you have given a passing grade.</li>' +
                '   <li>students have failed to get a passing grade more than the configured maximum number of times.</li>' +
                '</ul>' +
                '<p>However you may have to close a group manually if no maximum number of tries have been configured, or if you want the current feedback to be stored as the final feedback for this group.</p>',
            buttons: Ext.Msg.YESNO,
            scope: this,
            closable: false,
            fn: function(buttonId) {
                if(buttonId == 'yes') {
                    this.assignmentgroup_recordcontainer.record.data.is_open = false;
                    this.assignmentgroup_recordcontainer.record.save({
                        scope: this,
                        success: function(record) {
                            this.assignmentgroup_recordcontainer.fireSetRecordEvent();
                        },
                        failure: function() {
                            throw "Failed to close group."
                        }
                    });
                }
                button.toggle(false);
            }
        });
        win.alignTo(button, 'bl', [0, 0]);
    },

    /**
     * @private
     */
    onDeadlines: function(button) {
        var deadlinesWindow = Ext.create('Ext.window.Window', {
            title: 'Deadlines for this group',
            width: 600,
            height: 400,
            modal: true,
            layout: 'fit',
            closeAction: 'hide',
            items: {
                xtype: 'deadlinesonsinglegrouplisting',
                assignmentgroup_recordcontainer: this.assignmentgroup_recordcontainer,
                delivery_recordcontainer: this.delivery_recordcontainer,
                deliverymodel: this.deliverymodel,
                deadlinemodel: this.deadlinemodel,
                enableDeadlineCreation: this.canExamine
            },
            listeners: {
                scope: this,
                close: function() {
                    button.toggle(false);
                }
            }
        });
        deadlinesWindow.show();
        deadlinesWindow.alignTo(button, 'bl', [0, 0]);
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
