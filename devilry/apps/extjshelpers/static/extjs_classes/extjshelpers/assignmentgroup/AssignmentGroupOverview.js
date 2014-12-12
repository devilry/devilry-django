/**
 *
 * Requires the following icnlude in the django template:
 *
 *     {% include "extjshelpers/AssignmentGroupOverviewExtjsClasses.django.html" %}
 */
Ext.define('devilry.extjshelpers.assignmentgroup.AssignmentGroupOverview', {
    extend: 'Ext.container.Container',
    alias: 'widget.assignmentgroupoverview',
    cls: 'widget-assignmentgroupoverview devilry_subtlebg',
    requires: [
        'devilry.extjshelpers.assignmentgroup.StaticFeedbackInfo',
        'devilry.extjshelpers.assignmentgroup.StaticFeedbackEditor',
        'devilry.extjshelpers.assignmentgroup.AssignmentGroupTitle',
        'devilry.extjshelpers.assignmentgroup.AssignmentGroupTodoListWindow',
        'devilry.extjshelpers.assignmentgroup.DeliveriesGroupedByDeadline',
        'devilry.extjshelpers.assignmentgroup.IsOpen',
        'devilry.extjshelpers.RestFactory',
        'devilry.administrator.models.Delivery',
        'devilry.examiner.models.Delivery',
        'devilry.student.models.Delivery',
        'devilry.extjshelpers.SingleRecordContainer',
        'devilry.extjshelpers.assignmentgroup.DeadlineExpiredNoDeliveriesBox'
    ],

    nonElectronicNodeTpl: Ext.create('Ext.XTemplate',
        '<div class="bootstrap">',
            '<div class="alert" style="margin: 0;">',
                '<p><strong>Warning</strong>: This assignment only uses Devilry for registering results, not for deliveries. ',
                'Deliveries are registered (by examiners) as a placeholder for results.</p>',
                '<tpl if="canExamine">',
                '   <p>See <a href="{DEVILRY_HELP_URL}" target="_blank">help</a> for details about how to correct non-electronic deliveries.</p>',
                '</tpl>',
            '</div>',
        '</div>'
    ),

    /**
     * @cfg {bool} [canExamine]
     * Enable creation of new feedbacks? Defaults to ``false``.
     *
     * When this is ``true``, the authenticated user still needs to have
     * permission to POST new feedbacks for the view to work.
     */
    canExamine: false,

    /**
     * @cfg {int} [assignmentgroupid]
     * AssignmentGroup ID.
     */
    assignmentgroupid: undefined,

    /**
     * @cfg {bool} [isAdministrator]
     * Use the administrator RESTful interface to store drafts? If this is
     * ``false``, we use the examiner RESTful interface.
     */
    isAdministrator: false,


    autoScroll: true,


    constructor: function() {
        this.addEvents('assignmentGroupLoaded');
        this.callParent(arguments);
    },


    initComponent: function() {
        this.assignmentgroup_recordcontainer = Ext.create('devilry.extjshelpers.SingleRecordContainer');
        this.delivery_recordcontainer = Ext.create('devilry.extjshelpers.SingleRecordContainer');
        this.gradeeditor_config_recordcontainer = Ext.create('devilry.extjshelpers.SingleRecordContainer');

        this.createAttributes();
        this.createLayout();
        this.callParent(arguments);
        this.loadAssignmentgroupRecord(); // NOTE: Must come after createLayout() because components listen for the setRecord event
    },

    /**
     * @private
     */
    createAttributes: function() {
        this.role = !this.canExamine? 'student': this.isAdministrator? 'administrator': 'examiner';
        this.assignmentgroupmodel = Ext.ModelManager.getModel(this.getSimplifiedClassName('SimplifiedAssignmentGroup'));
        this.filemetastore = this._createStore('SimplifiedFileMeta');
        this.staticfeedbackstore = this._createStore('SimplifiedStaticFeedback');
        this.deadlinemodel = Ext.ModelManager.getModel(this.getSimplifiedClassName('SimplifiedDeadline'));

        if(this.canExamine) {
            this.gradeeditor_config_model = Ext.ModelManager.getModel(Ext.String.format(
                'devilry.apps.gradeeditors.simplified.{0}.SimplifiedConfig',
                this.role
            ));
        }
    },


    _createStore: function(shortmodelname) {
        var modelname = this.getSimplifiedClassName(shortmodelname);
        var model = Ext.ModelManager.getModel(modelname);
        var store = Ext.create('Ext.data.Store', {
            model: model,
            remoteFilter: true,
            remoteSort: true,
            proxy: model.proxy.copy()
        });
        return store;
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
                this.fireEvent('assignmentGroupLoaded', record);
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
    _showFeedbackPanel: function() {
        if(this.delivery_recordcontainer.record && this.assignmentgroup_recordcontainer.record) {
            if(!this.feedbackPanel) {
                this.feedbackPanel = Ext.widget('staticfeedbackeditor', {
                    staticfeedbackstore: this.staticfeedbackstore,
                    delivery_recordcontainer: this.delivery_recordcontainer,
                    filemetastore: this.filemetastore,
                    assignmentgroup_recordcontainer: this.assignmentgroup_recordcontainer,
                    isAdministrator: this.isAdministrator, // Only required by staticfeedbackeditor
                    deadlinemodel: this.deadlinemodel, // Only required by staticfeedbackeditor
                    assignmentgroupmodel: this.assignmentgroupmodel, // Only required by staticfeedbackeditor
                    gradeeditor_config_recordcontainer: this.gradeeditor_config_recordcontainer // Only required by staticfeedbackeditor
                });
                this.centerArea.removeAll();
                this.centerArea.add(this.feedbackPanel);
            }
        }
    },

    _showNonElectronicNote: function() {
        if(this.assignmentgroup_recordcontainer.record.get('parentnode__delivery_types') === 1) {
            this.nonElectronicNote.show();
        }
    },

    /**
     * @private
     */
    createLayout: function() {
        if(this.delivery_recordcontainer.record) {
            this._showFeedbackPanel();
        } else {
            this.delivery_recordcontainer.addListener('setRecord', this._showFeedbackPanel, this);
        }
        if(this.assignmentgroup_recordcontainer.record) {
            this._showFeedbackPanel();
            this._showNonElectronicNote();
        } else {
            this.assignmentgroup_recordcontainer.addListener('setRecord', this._showFeedbackPanel, this);
            this.assignmentgroup_recordcontainer.addListener('setRecord', this._showNonElectronicNote, this);
        }

        Ext.apply(this, {
            layout: 'anchor',
            padding: '20 30 20 30',
            defaults: {anchor: '100%'},
            items: [{
                xtype: 'deadlineExpiredNoDeliveriesBox',
                hidden: true,
                listeners: {
                    scope: this,
                    closeGroup: this._onCloseGroup,
                    addDeadline: this._onCreateNewDeadline
                }
            }, {
                xtype: 'container',
                layout: 'column',
                items: [{
                    columnWidth: 1,
                    xtype: 'assignmentgrouptitle',
                    singlerecordontainer: this.assignmentgroup_recordcontainer,
                    margin: '0 0 10 0',
                    extradata: {
                        canExamine: this.canExamine,
                        url: window.location.href
                    }
                }, {
                    xtype: 'container',
                    width: 350,
                    layout: 'column',
//                    defaults: {anchor: '100%'},
                    items: [{
                        xtype: 'assignmentgroup_isopen',
                        columnWidth: 0.6,
                        assignmentgroup_recordcontainer: this.assignmentgroup_recordcontainer,
                        canExamine: this.canExamine
                    }, {
                        xtype: 'button',
                        columnWidth: 0.4,
                        hidden: !this.canExamine,
                        text: '<i class="icon-white icon-th-list"></i> ' + gettext('To-do list'),
                        cls: 'bootstrap',
                        scale: 'medium',
                        ui: 'inverse',
                        margin: '0 0 0 3',
                        listeners: {
                            scope: this,
                            click: function() {
                                Ext.create('devilry.extjshelpers.assignmentgroup.AssignmentGroupTodoListWindow', {
                                    assignmentgroupmodelname: this.getSimplifiedClassName('SimplifiedAssignmentGroup'),
                                    assignmentgroup_recordcontainer: this.assignmentgroup_recordcontainer
                                }).show();
                            }
                        }
                    }]
                }]
            }, {
                xtype: 'container',
                layout: 'column',
                style: 'background-color: transparent',
                flex: 1,
                border: false,
                items: [{
                    xtype: 'container',
                    margin: '0 40 0 0',
                    columnWidth: 0.3,
                    layout: 'anchor',
                    defaults: {anchor: '100%'},
                    items: [{
                        xtype: 'container',
                        margin: '8 0 0 0',
                        flex: 1,
                        border: false,
                        layout: {
                            type: 'vbox',
                            align: 'stretch'
                        },
                        items: [this.nonElectronicNote = Ext.widget('box', {
                            margin: '0 0 10 0',
                            hidden: true,
                            cls: 'readable-section',
                            html: this.nonElectronicNodeTpl.apply({canExamine: this.canExamine, DEVILRY_HELP_URL: DevilrySettings.DEVILRY_HELP_URL})
                        }), {
                            xtype: 'deliveriesgroupedbydeadline',
                            minHeight: 40,
                            role: this.role,
                            assignmentgroup_recordcontainer: this.assignmentgroup_recordcontainer,
                            delivery_recordcontainer: this.delivery_recordcontainer,
                            flex: 1,
                            listeners: {
                                scope: this,
                                loadComplete: this._selectAppropriateDelivery,
                                expiredNoDeliveries: this._onExpiredNoDeliveries,
                                createNewDeadline: this._onCreateNewDeadline
                            }
                        }]
                    }]
                }, this.centerArea = Ext.widget('container', {
                    columnWidth: 0.7,
                    layout: 'fit',
                    items: {
                        xtype: 'box',
                        html: ''
                    }
                })]
            }]
        });
    },

    /**
     * @private
     *
     * Select most natural delivery:
     *  - The one with active feedback
     *  - ... unless a delivery with timestamp after the latest feedback.
     */
    _selectMostNaturalDelivery: function(deliveriesgroupedbydeadline) {
        var latestDelivery = deliveriesgroupedbydeadline.getLatestDelivery();
        if(!latestDelivery) {
            return;
        }
        if(deliveriesgroupedbydeadline.latestStaticFeedbackRecord) {
            var latestFeedbackTime = deliveriesgroupedbydeadline.latestStaticFeedbackRecord.get('save_timestamp');
            if(latestDelivery.get('time_of_delivery') > latestFeedbackTime) {
                deliveriesgroupedbydeadline.selectDelivery(latestDelivery.get('id'));
            } else {
                deliveriesgroupedbydeadline.selectDelivery(deliveriesgroupedbydeadline.latestStaticFeedbackRecord.get('delivery'));
            }
        } else {
            deliveriesgroupedbydeadline.selectDelivery(latestDelivery.get('id'));
        }
    },

    _selectAppropriateDelivery: function(deliveriesgroupedbydeadline) {
        var query = Ext.Object.fromQueryString(window.location.search);
        if(query.deliveryid) {
            deliveriesgroupedbydeadline.selectDelivery(query.deliveryid);
        } else {
            this._selectMostNaturalDelivery(deliveriesgroupedbydeadline);
        }
    },


    /**
     * @private
     */
    _onCreateNewDeadline: function() {
        var me = this;
        var createDeadlineWindow = Ext.widget('createnewdeadlinewindow', {
            assignmentgroupid: this.assignmentgroup_recordcontainer.record.data.id,
            deadlinemodel: Ext.String.format('devilry.{0}.models.Deadline', this.role),
            onSaveSuccess: function(record) {
                this.close();
//                me.loadAllDeadlines();
                window.location.reload();
            }
        });
        createDeadlineWindow.show();
    },

    _onCloseGroup:function () {
        devilry.extjshelpers.assignmentgroup.IsOpen.closeGroup(this.assignmentgroup_recordcontainer, function() {
            window.location.reload();
        });
    },


    /**
     * @private
     */
    _onExpiredNoDeliveries: function() {
        var group = this.assignmentgroup_recordcontainer.record;
        if(group.get('is_open')) {
            this.down('deadlineExpiredNoDeliveriesBox').show();
        }
    }
});
