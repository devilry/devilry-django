/** The feedback creation methods for StudentsManager. */
Ext.define('devilry.extjshelpers.studentsmanager.StudentsManagerCreateFeedback', {

    requires: [
        'devilry.gradeeditors.RestfulRegistryItem'
    ],

    /**
     * @private
     */
    loadGradeEditorConfigModel: function() {
        this.gradeeditor_config_model.load(this.assignmentid, {
            scope: this,
            success: function(configRecord) {
                this.gradeeditor_config_recordcontainer.setRecord(configRecord);
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
            success: function(registryItemRecord) {
                this.registryitem_recordcontainer.setRecord(registryItemRecord);
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
        this.progressWindow.start('Give feedback to many');
        this._finishedSavingGroupCount = 0;
        this.down('studentsmanager_studentsgrid').gatherSelectedRecordsInArray({
            scope: this,
            callback: function(groupRecords) {
                if(this.assignmentrecord.data.delivery_types === this.deliveryTypes.TYPE_ELECTRONIC && this.anyGroupHaveNoDeliveries(groupRecords)) {
                    Ext.MessageBox.show({
                        title: 'Selected groups with no deliveries',
                        msg: 'One or more of the selected groups have no deliveries. You can only give feedback to groups with deliveries. Please review your selection and try again.',
                        buttons: Ext.Msg.OK,
                        icon: Ext.Msg.ERROR
                    });
                } else {
                    Ext.each(groupRecords, function(groupRecord, index) {
                        this.giveFeedbackToSelected(groupRecord, index, groupRecords.length, feedbackdraftModelName, draftstring);
                    }, this);
                }
            }
        });
    },

    /**
     * @private
     */
    anyGroupHaveNoDeliveries: function(groupRecords) {
        for(i=0; i<groupRecords.length; i++) {
            var groupRecord = groupRecords[i];
            if(groupRecord.data.number_of_deliveries === 0) {
                return true;
            }
        }
        return false;
    },

    /**
     * @private
     */
    giveFeedbackToSelected: function(assignmentGroupRecord, index, totalSelectedGroups, feedbackdraftModelName, draftstring) {
        var msg = Ext.String.format('Setting feedback on group {0}/{1}', index, totalSelectedGroups);
        this.getEl().mask(msg);

        if(assignmentGroupRecord.data.latest_delivery_id === null)  {
            if(this.assignmentrecord.data.delivery_types === this.deliveryTypes.TYPE_ELECTRONIC) {
                this.progressWindow.addWarning(assignmentGroupRecord, 'Has no deliveries, and therefore we can not add any feedback.');
                this._finishedSavingGroupCount ++;
                this.checkIfFinishedGivingFeedback(totalSelectedGroups);
            } else {
                var delivery = this.createDeliveryRecord(assignmentGroupRecord, this.deliveryTypes.TYPE_NON_ELECTRONIC);
                delivery.save({
                    scope: this,
                    callback: function(deliveryrecord, operation) {
                        if(operation.success) {
                            this.progressWindow.addSuccess(assignmentGroupRecord, 'Non-electronic delivery successfully registered.');
                            this.publishFeedbackOnDelivery(assignmentGroupRecord, deliveryrecord.data.id, totalSelectedGroups, feedbackdraftModelName, draftstring);
                        } else {
                            this.progressWindow.addErrorFromOperation(
                                assignmentGroupRecord, 'Failed to register non-electronic delivery', operation
                            );
                            this.checkIfFinishedGivingFeedback(totalSelectedGroups);
                        }
                    }
                });
            }
        } else {
            this.publishFeedbackOnDelivery(assignmentGroupRecord, assignmentGroupRecord.data.latest_delivery_id, totalSelectedGroups, feedbackdraftModelName, draftstring);
        }
    },

    /**
     * @private
     */
    publishFeedbackOnDelivery: function(assignmentGroupRecord, delivery_id, totalSelectedGroups, feedbackdraftModelName, draftstring) {
        var draftrecord = Ext.create(feedbackdraftModelName, {
            draft: draftstring,
            published: true,
            delivery: delivery_id
        });
        draftrecord.save({
            scope: this,
            callback: function(r, operation) {
                if(operation.success) {
                    this.progressWindow.addSuccess(assignmentGroupRecord, 'Feedback successfully created.');
                } else {
                    this.progressWindow.addErrorFromOperation(
                        assignmentGroupRecord, 'Failed to create feedback', operation
                    );
                }

                this._finishedSavingGroupCount ++;
                this.checkIfFinishedGivingFeedback(totalSelectedGroups);
            }
        });
    },


    checkIfFinishedGivingFeedback: function(totalSelectedGroups) {
        if(this._finishedSavingGroupCount == totalSelectedGroups) {
            this.loadFirstPage();
            this.getEl().unmask();
            this.progressWindow.finish();
        }
    }
});
