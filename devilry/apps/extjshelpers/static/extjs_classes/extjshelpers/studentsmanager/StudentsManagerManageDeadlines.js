/** The deadline management methods for StudentsManager.
 *
 * Note that this class depends on createRecordFromStoreRecord(),
 * onSelectNone() and loadFirstPage() from StudentsManager to be available. */
Ext.define('devilry.extjshelpers.studentsmanager.StudentsManagerManageDeadlines', {
    requires: [
        'devilry.extjshelpers.assignmentgroup.MultiCreateNewDeadlineWindow'
    ],

    /**
     * @private
     */
    onAddDeadline: function() {
        //this.down('studentsmanager_studentsgrid').selModel.selectAll();
        if(this.noneSelected()) {
            this.onSelectNone();
            return;
        }
        var me = this;
        var createDeadlineWindow = Ext.widget('multicreatenewdeadlinewindow', {
            deadlinemodel: this.deadlinemodel,
            onSaveSuccess: function(record) {
                this.close();
                me.addDeadlineToSelected(record);
            }
        });
        createDeadlineWindow.show();
    },

    /**
     * @private
     */
    addDeadlineToSelected: function(record) {
        this.progressWindow.start('Add deadline');
        this._finishedSavingGroupCount = 0;
        this.down('studentsmanager_studentsgrid').performActionOnSelected({
            scope: this,
            callback: this.addDeadline,
            extraArgs: [record]
        });
    },

    /**
     * @private
     */
    addDeadline: function(assignmentGroupRecord, index, totalSelectedGroups, deadlineRecord) {
        var msg = Ext.String.format('Adding deadline to group {0}/{1}', index, totalSelectedGroups);
        this.getEl().mask(msg);

        this.statics().createDeadline(assignmentGroupRecord, deadlineRecord, this.deadlinemodel, {
            scope: this,
            callback: function(r, operation) {
                if(operation.success) {
                    this.progressWindow.addSuccess(assignmentGroupRecord, 'Deadline successfully created.');
                } else {
                    this._onAddDeadlineFailure(assignmentGroupRecord, operation);
                }

                this._finishedSavingGroupCount ++;
                if(this._finishedSavingGroupCount == totalSelectedGroups) {
                    this.loadFirstPage();
                    this.getEl().unmask();
                    this.progressWindow.finish();
                }
            }
        });

        if(index == totalSelectedGroups) {
            this.loadFirstPage();
            this.getEl().unmask();
        }
    },

    _onAddDeadlineFailure: function(assignmentGroupRecord, operation) {
        this.progressWindow.addErrorFromOperation(
            assignmentGroupRecord, 'Failed to create deadline', operation
        );
    },

    statics: {
        createDeadline: function(assignmentGroupRecord, deadlineRecord, deadlinemodel, saveopt) {
            var newDeadlineRecord = Ext.ModelManager.create(deadlineRecord.data, deadlinemodel);
            newDeadlineRecord.data.assignment_group = assignmentGroupRecord.data.id;
            newDeadlineRecord.save(saveopt);
        }
    }
});
