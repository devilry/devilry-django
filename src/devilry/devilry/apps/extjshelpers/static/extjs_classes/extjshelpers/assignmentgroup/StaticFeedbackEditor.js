/** Panel to show StaticFeedback info and create new static feedbacks.
 */
Ext.define('devilry.extjshelpers.assignmentgroup.StaticFeedbackEditor', {
    extend: 'devilry.extjshelpers.assignmentgroup.StaticFeedbackInfo',
    alias: 'widget.staticfeedbackeditor',
    requires: [
        'devilry.gradeeditors.DraftEditorWindow',
        'devilry.gradeeditors.RestfulRegistryItem',
        'devilry.extjshelpers.assignmentgroup.CreateNewDeadlineWindow'
    ],

    config: {
        /**
         * @cfg
         * A {@link devilry.extjshelpers.SingleRecordContainer} for GradeEditor Config.
         */
        gradeeditor_config_recordcontainer: undefined,

        /**
         * @cfg
         * Use the administrator RESTful interface to store drafts? If this is
         * ``false``, we use the examiner RESTful interface.
         */
        isAdministrator: false,

        assignmentgroupmodel: undefined,
        deadlinemodel: undefined
    },

    constructor: function(config) {
        return this.callParent([config]);
    },

    initComponent: function() {
        this.callParent(arguments);

        this.staticfeedback_recordcontainer.addListener('setRecord', this.onSetStaticFeedbackRecordInEditor, this);
        this.on('afterStoreLoadMoreThanZero', this.onAfterStoreLoadMoreThanZero, this);

        if(this.gradeeditor_config_recordcontainer.record) {
            this.onLoadGradeEditorConfig();
        }
        this.gradeeditor_config_recordcontainer.addListener('setRecord', this.onLoadGradeEditorConfig, this);

        this.registryitem_recordcontainer = Ext.create('devilry.extjshelpers.SingleRecordContainer');
        this.registryitem_recordcontainer.addListener('setRecord', this.onLoadRegistryItem, this);

        this.assignmentgroup_recordcontainer.addListener('setRecord', this.enableEditButton, this);

        if(this.delivery_recordcontainer.record) {
            this.onLoadDeliveryInEditor();
        }
        this.delivery_recordcontainer.on('setRecord', this.onLoadDeliveryInEditor, this);
    },


    getToolbarItems: function() {
        this.createButton = Ext.create('Ext.button.Button', {
            text: 'Create feedback',
            iconCls: 'icon-add-32',
            hidden: false,
            scale: 'large',
            listeners: {
                scope: this,
                click: this.loadGradeEditor,
                render: this.onRenderEditButton
            }
        });
        var defaultItems = this.callParent();
        Ext.Array.insert(defaultItems, 0, [this.createButton]);
        return defaultItems;
    },


    /**
     * @private
     */
    onAfterStoreLoadMoreThanZero: function() {
        this.enableEditButton();
        if(this.editFeedbackTip) {
            this.editFeedbackTip.hide();
        }
    },

    /**
     * @private
     */
    onRenderEditButton: function(button) {
        //var id = button.getEl().id
        Ext.defer(function() {
            if(!this.isReadyToEditFeedback()) {
                button.getEl().mask('Loading...');
            }
        }, 100, this);
        this.editFeedbackTip = Ext.create('Ext.tip.ToolTip', {
            title: 'Click to give feedback on this delivery',
            anchor: 'top',
            target: button.getEl().id,
            html: 'You add feedback to a specific delivery. The latest feedback you publish on any delivery on this assignment becomes their active feedback/grade on the assignment.',
            width: 415,
            dismissDelay: 35000,
            autoHide: true
        });
    },

    /**
     * @private
     */
    showNoFeedbackTip: function() {
        if(this.editFeedbackTip) {
            this.editFeedbackTip.show();
        } else {
            Ext.defer(function() {
                this.showNoFeedbackTip();
            }, 300, this);
        }
    },

    /**
     * @private
     * This is suffixed with InEditor to not crash with superclass.onLoadDelivery().
     */
    onLoadDeliveryInEditor: function() {
        this.enableEditButton();
    },

    /**
     * @private
     */
    onLoadGradeEditorConfig: function() {
        this.loadRegistryItem();
    },

    /**
     * @private
     */
    loadRegistryItem: function() {
        var registryitem_model = Ext.ModelManager.getModel('devilry.gradeeditors.RestfulRegistryItem');
        registryitem_model.load(this.gradeeditor_config_recordcontainer.record.data.gradeeditorid, {
            scope: this,
            success: function(record) {
                this.registryitem_recordcontainer.setRecord(record);
            }
        });
    },

    /**
     * @private
     */
    onLoadRegistryItem: function() {
        this.enableEditButton();
    },

    /**
     * @private
     * Show create button when:
     *
     * - Delivery has loaded.
     * - Grade editor config has loaded.
     * - Registry item has loaded.
     */
    enableEditButton: function() {
        if(this.isReadyToEditFeedback()) {
            this.createButton.getEl().unmask();
        }
    },

    /**
     * @private
     */
    isReadyToEditFeedback: function() {
        return this.gradeeditor_config_recordcontainer.record &&
                this.delivery_recordcontainer.record &&
                this.registryitem_recordcontainer.record &&
                this.assignmentgroup_recordcontainer.record;
    },

    /**
     * @private
     */
    loadGradeEditor: function() {
        Ext.widget('gradedrafteditormainwin', {
            deliveryid: this.delivery_recordcontainer.record.data.id,
            isAdministrator: this.isAdministrator,
            gradeeditor_config: this.gradeeditor_config_recordcontainer.record.data,
            registryitem: this.registryitem_recordcontainer.record.data,
            listeners: {
                scope: this,
                publishNewFeedback: this.onPublishNewFeedback
            }
        }).show();
    },

    /**
     * Overrides parent method to enable examiners to click to create feedback.
     */
    bodyWithNoFeedback: function() {
        var me = this;
        this.setBody({
            xtype: 'component',
            html: ''
        });
        this.showNoFeedbackTip();
        //this.setBody({
            //xtype: 'component',
            //cls: 'no-feedback-editable',
            //html: '<p class="no-feedback-message">No feedback</p><p class="click-create-create-feedback-message">Click to create feedback</p>',
            //listeners: {
                //render: function() {
                    //this.getEl().addListener('mouseup', me.loadGradeEditor, me);
                //}
            //}
        //});
    },

    /**
     * @private
     */
    onPublishNewFeedback: function() {
        this.hasNewPublishedStaticFeedback = true;
        this.onLoadDelivery();
    },

    /**
     * @private
     */
    onSetStaticFeedbackRecordInEditor: function() {
        if(this.hasNewPublishedStaticFeedback) {
            this.hasNewPublishedStaticFeedback = false;
            this.onNewPublishedStaticFeedback();
        }
    },

    /**
     * @private
     */
    onNewPublishedStaticFeedback: function() {
        var staticfeedback = this.staticfeedback_recordcontainer.record.data;
        if(staticfeedback.is_passing_grade) {
            this.reloadAssignmentGroup();
        } else {
            this.onFailingGrade();
        }
    },

    /**
     * @private
     */
    reloadAssignmentGroup: function() {
        this.assignmentgroupmodel.load(this.assignmentgroup_recordcontainer.record.data.id, {
            scope: this,
            success: function(record) {
                this.assignmentgroup_recordcontainer.setRecord(record);
            },
            failure: function() {
                // TODO: Handle errors
            }
        });
    },

    /**
     * @private
     */
    onFailingGrade: function() {
        var win = Ext.MessageBox.show({
            title: 'You published a feedback with a failing grade',
            msg: '<p>Would you like to give the group another try?</p><ul>' +
                '<li>Choose <strong>yes</strong> to create a new deadline</li>' +
                '<li>Choose <strong>no</strong> to close the group. This fails the student on this assignment. You can re-open the group at any time.</li>' +
                '</ul>',
            buttons: Ext.Msg.YESNO,
            scope: this,
            closable: false,
            fn: function(buttonId) {
                if(buttonId == 'yes') {
                    this.createNewDeadline();
                } else {
                    this.reloadAssignmentGroup();
                }
            }
        });
    },

    /**
     * @private
     */
    createNewDeadline: function() {
        var me = this;
        var createDeadlineWindow = Ext.widget('createnewdeadlinewindow', {
            assignmentgroupid: this.assignmentgroup_recordcontainer.record.data.id,
            deadlinemodel: this.deadlinemodel,
            onSaveSuccess: function(record) {
                me.reloadAssignmentGroup();
                this.close();
            }
        });
        createDeadlineWindow.show();
    }
});
