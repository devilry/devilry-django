/** The feedback creation methods for StudentsManager. */
Ext.define('devilry.extjshelpers.studentsmanager.StudentsManagerCreateFeedback', {
    /**
     * @private
     */
    loadGradeEditorConfigModel: function() {
        this.gradeeditor_config_model.load(this.assignmentid, {
            scope: this,
            success: function(record) {
                this.gradeeditor_config_recordcontainer.setRecord(record);
                this.loadRegistryItem();
            },
            failure: function() {
                // TODO: Handle errors
            }
        });
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
        if(this.giveFeedbackButton.rendered) {
            this.giveFeedbackButton.getEl().unmask();
        }
    },

    /**
     * @private
     */
    onGiveFeedbackToSelected: function(button) {
        if(this.noneSelected()) {
            this.onSelectNone();
            return;
        }
        var draftEditor = Ext.create('devilry.gradeeditors.EditManyDraftEditorWindow', {
            isAdministrator: this.isAdministrator,
            gradeeditor_config: this.gradeeditor_config_recordcontainer.record.data,
            registryitem: this.registryitem_recordcontainer.record.data,
            listeners: {
                scope: this,
                createNewDraft: this.onPublishFeedback
            }
        });
        draftEditor.show();
    },


    /**
     * @private
     */
    onPublishFeedback: function(feedbackdraftModelName, draftstring) {
        //this.down('studentsmanager_studentsgrid').selModel.selectAll();
        this.down('studentsmanager_studentsgrid').performActionOnSelected({
            scope: this,
            callback: this.giveFeedbackToSelected,
            extraArgs: [feedbackdraftModelName, draftstring]
        });
    },

    /**
     * @private
     */
    giveFeedbackToSelected: function(record, index, total, feedbackdraftModelName, draftstring) {
        var msg = Ext.String.format('Setting feedback on group {0}/{1}', index, total);
        this.getEl().mask(msg);

        if(record.data.latest_delivery_id != null) {
            var draftrecord = Ext.create(feedbackdraftModelName, {
                draft: draftstring,
                published: true,
                delivery: record.data.latest_delivery_id
            });
            draftrecord.save({
                scope: this,
                failure: function() {
                    console.error('Failed to save a draft');
                    console.error(draftrecord);
                }
            });
        }

        if(index == total) {
            this.loadFirstPage();
            this.getEl().unmask();
        }
    }
});
