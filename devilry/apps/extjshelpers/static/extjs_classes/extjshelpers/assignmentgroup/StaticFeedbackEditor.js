/** Panel to show StaticFeedback info and create new static feedbacks.
 */
Ext.define('devilry.extjshelpers.assignmentgroup.StaticFeedbackEditor', {
    extend: 'devilry.extjshelpers.assignmentgroup.StaticFeedbackInfo',
    alias: 'widget.staticfeedbackeditor',
    requires: [
        'devilry.gradeeditors.DraftEditorWindow',
        'devilry.gradeeditors.RestfulRegistryItem'
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

        assignmentgroup_recordcontainer: undefined
    },

    constructor: function(config) {
        return this.callParent([config]);
    },

    initComponent: function() {
        this.callParent(arguments);

        this.staticfeedback_recordcontainer.addListener('setRecord', this.onSetStaticFeedbackRecordInEditor, this);

        var me = this;
        this.createButton = Ext.create('Ext.button.Button', {
            text: 'Edit feedback',
            //iconCls: 'icon-edit-32',
            hidden: true,
            scale: 'large',
            listeners: {
                scope: this,
                click: this.loadGradeEditor
            }
        });
        this.editToolbar.add(this.createButton);

        this.addListener('afterStoreLoadMoreThanZero', this.showCreateButton, this);

        if(this.delivery_recordcontainer.record) {
            this.onLoadDeliveryInEditor();
        }
        this.delivery_recordcontainer.addListener('setRecord', this.onLoadDeliveryInEditor, this);

        if(this.gradeeditor_config_recordcontainer.record) {
            this.onLoadGradeEditorConfig();
        }
        this.gradeeditor_config_recordcontainer.addListener('setRecord', this.onLoadGradeEditorConfig, this);

        this.registryitem_recordcontainer = Ext.create('devilry.extjshelpers.SingleRecordContainer');
        this.registryitem_recordcontainer.addListener('setRecord', this.onLoadRegistryItem, this);

    },

    /**
     * @private
     * This is suffixed with InEditor to not crash with superclass.onLoadDelivery().
     */
    onLoadDeliveryInEditor: function() {
        this.showCreateButton();
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
        this.showCreateButton();
    },

    /**
     * @private
     * Show create button when:
     *
     * - Delivery has loaded.
     * - Grade editor config has loaded.
     * - Registry item has loaded.
     */
    showCreateButton: function() {
        if(this.gradeeditor_config_recordcontainer.record &&
                this.delivery_recordcontainer.record &&
                this.registryitem_recordcontainer.record) {
            this.createButton.show();
        }
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
            cls: 'no-feedback-editable',
            html: '<p>No feedback</p><p class="unimportant">Click to create feedback</p>',
            listeners: {
                render: function() {
                    this.getEl().addListener('mouseup', me.loadGradeEditor, me);
                }
            }
        });
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
            this.closeAssignmentGroup();
        } else {
            this.onFailingGrade();
        }
    },

    /**
     * @private
     */
    closeAssignmentGroup: function() {
        this.assignmentgroup_recordcontainer.record.data.is_open = false;
        this.assignmentgroup_recordcontainer.record.save({
            scope: this,
            success: function(record) {
                // TODO: Notify about closing the group
                this.assignmentgroup_recordcontainer.fireSetRecordEvent();
            },
            failure: function() {
                throw "Failed to close group."
            }
        });
    },

    /**
     * @private
     */
    onFailingGrade: function() {
        console.log('failing grade...');
    }
});
