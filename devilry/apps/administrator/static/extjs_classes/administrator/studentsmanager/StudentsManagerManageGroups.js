/** The group management methods for StudentsManager. */
Ext.define('devilry.administrator.studentsmanager.StudentsManagerManageGroups', {
    requires: [
        'devilry.administrator.studentsmanager.ManuallyCreateUsers',
        'devilry.extjshelpers.RestProxy'
    ],

    /**
     * @private
     */
    showCreateGroupsInBulkWindow: function(initialLines, currentGroupRecords) {
        var win = Ext.widget('window', {
            title: 'Create assignment groups',
            modal: true,
            width: 830,
            height: 600,
            maximizable: true,
            layout: 'fit',
            items: {
                xtype: 'manuallycreateusers',
                deadlinemodel: this.deadlinemodel,
                assignmentrecord: this.assignmentrecord,
                suggestedDeadline: this.guessDeadlineFromCurrentlyLoadedGroups(),
                currentGroupRecords: currentGroupRecords,
                initialLines: initialLines
            },
            listeners: {
                scope: this,
                close: function() {
                    this.refreshStore();
                }
            }
        });
        win.show();
    },

    /**
     * @private
     */
    createManyGroupsInBulk: function(initialLines) {
        this.getEl().mask('Loading current assignment groups...');
        devilry.administrator.studentsmanager.StudentsManager.getAllGroupsInAssignment(this.assignmentid, {
            scope: this,
            callback: function(records, op, success) {
                this.getEl().unmask();
                if(success) {
                    this.showCreateGroupsInBulkWindow(initialLines, records);
                } else {
                    Ext.MessageBox.alert('Failed to load current assignment groups. Please try again.');
                }
            }
        });
    },

    /**
     * @private
     *
     * Pick the latest deadline on the last group in the current view. The idea
     * is to get the last created group, however we do not load the last page,
     * so this is a balance of efficiency and convenience.
     */
    guessDeadlineFromCurrentlyLoadedGroups: function() {
        var groupRecords = this.assignmentgroupstore.data.items;
        if(groupRecords.length > 0) {
            var lastLoadedGroup = groupRecords[groupRecords.length-1];
            return lastLoadedGroup.data.latest_deadline_deadline;
        } else {
            return undefined;
        }
    },

    /**
     * @private
     */
    onManuallyCreateUsers: function() {
        this.createManyGroupsInBulk();
    },

    /**
     * @private
     */
    onOneGroupForEachRelatedStudent: function() {
        this.loadAllRelatedStudents({
            scope: this,
            callback: this.createOneGroupForEachRelatedStudent
            //args: ['Hello world']
        });
    },

    /**
     * @private
     */
    createOneGroupForEachRelatedStudent: function(relatedStudents) {
        this.createManyGroupsInBulk(this.relatedUserRecordsToArray(relatedStudents));
    },


    onChangeGroupName: function() {
        if(!this.singleSelected()) {
            this.onNotSingleSelected();
            return;
        }

        var record = this.getSelection()[0];
        Ext.Msg.prompt('Change group name', 'Please enter a new group name:', function(btn, name){
            if (btn == 'ok'){
                record.data.name = name;
                record.save();
            }
        });
    },

    onChangeGroupMembers: function() {
        if(!this.singleSelected()) {
            this.onNotSingleSelected();
            return;
        }

        var record = this.getSelection()[0];
        var candidates = this.statics().getCandidateInfoFromGroupRecord(record);

        var candidatestrings = [];
        var statics = this.statics();
        Ext.each(candidates, function(candidate, index) {
            candidatestrings.push(statics.formatCandidateInfoAsString(candidate));
        });

        var win = Ext.widget('window', {
            title: 'Select members',
            modal: true,
            width: 500,
            height: 400,
            maximizable: true,
            layout: 'fit',
            items: {
                xtype: 'setlistofusers',
                usernames: candidatestrings,
                anonymous: record.data.parentnode__anonymous,
                helptpl: Ext.create('Ext.XTemplate',
                    '<div class="section helpsection">',
                    '   <tpl if="anonymous">',
                    '       <p>One candidate of on each line. Username and <em>candidate ID</em> is separated by a single colon. Note that <em>candidate ID</em> does not have to be a number.</p>',
                    '       <p>Example:</p>',
                    '       <pre style="padding: 5px;">bob:20\nalice:A753\neve:SEC-01\ndave:30</pre>',
                    '   </tpl>',
                    '   <tpl if="!anonymous">',
                    '       <p>One username on each line. Example</p>',
                    '       <pre style="padding: 5px;">bob\nalice\neve\ndave</pre>',
                    '   </tpl>',
                    '</div>'
                ),
                listeners: {
                    scope: this,
                    saveClicked: Ext.bind(this.changeGroupMembers, this, [record], true)
                }
            },
        });
        win.show();
    },

    changeGroupMembers: function(setlistofusersobj, candidateSpecs, caller, record) {
        var editRecord = this.createRecordFromStoreRecord(record);
        editRecord.data.fake_candidates = [];
        Ext.Array.each(candidateSpecs, function(candidateSpec) {
            editRecord.data.fake_candidates.push(devilry.administrator.studentsmanager.StudentsManagerManageGroups.parseCandidateSpec(candidateSpec));
        }, this);

        setlistofusersobj.getEl().mask("Changing group members");
        editRecord.save({
            scope: this,
            failure: function(records, operation) {
                setlistofusersobj.getEl().unmask();
                devilry.extjshelpers.RestProxy.showErrorMessagePopup(operation, 'Failed to change group members');
            },
            success: function() {
                setlistofusersobj.up('window').close();
                this.loadFirstPage();
            }
        });
    },

    onDeleteGroups: function() {
        //this.down('studentsmanager_studentsgrid').selModel.selectAll();
        if(this.noneSelected()) {
            this.onSelectNone();
            return;
        }
        Ext.MessageBox.show({
            title: 'Are you sure that you want to delete the selected groups',
            msg: '<p>Are you sure you want to delete the selected groups?</p><p>If you are a <strong>superadmin</strong>, this will delete the group and all their related data on this assignment, including deliveries and feedback.</p><p>If you are a normal administrator, you will only be permitted to delete groups without any deliveries.</p>',
            buttons: Ext.Msg.YESNO,
            icon: Ext.Msg.WARNING,
            scope: this,
            fn: function(btn) {
                if(btn == 'yes') {
                    this.down('studentsmanager_studentsgrid').gatherSelectedRecordsInArray({
                        scope: this,
                        callback: this.deleteGroups
                    });
                }
            }
        });

    },

    /**
     * @private
     */
    deleteGroups: function(groupRecords) {
        this.progressWindow.start('Delete groups');
        this._finishedSavingGroupCount = 0;
        Ext.each(groupRecords, function(groupRecord, index) {
            this.deleteGroup(groupRecord, index, groupRecords.length);
        }, this);
    },

    /**
     * @private
     */
    deleteGroup: function(record, index, totalSelectedGroups) {
        var msg = Ext.String.format('Deleting group {0}/{1}',
            index, totalSelectedGroups
        );
        this.getEl().mask(msg);

        var editRecord = this.createRecordFromStoreRecord(record);
        editRecord.destroy({
            scope: this,
            callback: function(r, operation) {
                if(operation.success) {
                    this.progressWindow.addSuccess(record, 'Group successfully deleted.');
                } else {
                    this.progressWindow.addErrorFromOperation(record, 'Failed to delete group.', operation);
                }

                this._finishedSavingGroupCount ++;
                if(this._finishedSavingGroupCount == totalSelectedGroups) {
                    this.loadFirstPage();
                    this.getEl().unmask();
                    this.progressWindow.finish();
                }
            }
        });
    },

    
    onImportGroupsFromAnotherAssignmentInCurrentPeriod: function() {
        Ext.widget('window', {
            title: 'Import from another assignment in the current Period',
            layout: 'fit',
            width: 830,
            height: 600,
            modal: true,
            items: {
                xtype: 'importgroupsfromanotherassignment',
                periodid: this.periodid,
                help: '<div class="section helpsection">Select the assignment you wish to import assignment groups from, and click <em>Next</em> to further edit the selected groups.</div>',
                listeners: {
                    scope: this,
                    next: this.importGroupsFromAnotherAssignmentInCurrentPeriod
                }
            }
        }).show();
    },

    importGroupsFromAnotherAssignmentInCurrentPeriod: function(importPanel, assignmentGroupRecords) {
        importPanel.up('window').close();
        var statics = this.statics();
        var groups = [];
        Ext.each(assignmentGroupRecords, function(record, index) {
            var candidates = statics.getCandidateInfoFromGroupRecord(record);
            var groupString = '';
            Ext.each(candidates, function(candidate, index) {
                var candidateString = statics.formatCandidateInfoAsString(candidate);
                if(index != candidates.length-1)
                    candidateString += ', ';
                groupString += candidateString;
            });
            groups.push(groupString);
        });
        this.createManyGroupsInBulk(groups);
    },


    onSetCandidateIdBulk: function() {
        if(this.noneSelected()) {
            this.onSelectNone();
            return;
        }
        var win = Ext.widget('window', {
            title: 'Select members',
            modal: true,
            width: 500,
            height: 400,
            maximizable: true,
            layout: 'fit',
            items: {
                xtype: 'setlistofusers',
                usernames: [],
                anonymous: this.assignmentrecord.anonymous,
                helptpl: Ext.create('Ext.XTemplate',
                    '<div class="section helpsection">',
                    '   <tpl if="anonymous">',
                    '       <p>One candidate of on each line. Username and <em>candidate ID</em> is separated by a single colon. Note that <em>candidate ID</em> does not have to be a number.</p>',
                    '       <p>Example:</p>',
                    '       <pre style="padding: 5px;">bob:20\nalice:A753\neve:SEC-01\ndave:30</pre>',
                    '   </tpl>',
                    '   <tpl if="!anonymous">',
                    '       <p>One username on each line. Example</p>',
                    '       <pre style="padding: 5px;">bob\nalice\neve\ndave</pre>',
                    '   </tpl>',
                    '</div>'
                ),
                listeners: {
                    scope: this,
                    saveClicked: function(setlistofusersobj, candidateSpecs, caller) {
                        setlistofusersobj.up('window').close();
                        this.progressWindow.start('Set candidate ID on many');
                        this._finishedSavingGroupCount = 0;
                        this.down('studentsmanager_studentsgrid').performActionOnSelected({
                            scope: this,
                            callback: this.setCandidateId,
                            extraArgs: [this.parseCandidateImportFormat(candidateSpecs)]
                        });
                        
                    },
                }
            }
        });
        win.show();

    },

    /**
     * @private
     */
    parseCandidateImportFormat: function(candidateSpecs) {
        var usernameToCandidateIdMap = {};
        Ext.each(candidateSpecs, function(candidateSpec, index) {
            var s = candidateSpec.split(/\s*:\s*/);
            // TODO: Error checking
            usernameToCandidateIdMap[s[0]] = s[1];
        }, this);
        return usernameToCandidateIdMap;
    },

    /**
     * @private
     */
    setCandidateId: function(record, index, totalSelectedGroups, usernameToCandidateIdMap) {
        var msg = Ext.String.format('Setting candidate ID on group {0}/{1}',
            index, totalSelectedGroups
        );
        this.getEl().mask(msg);

        var editRecord = this.createRecordFromStoreRecord(record);
        console.log(usernameToCandidateIdMap, record);
        editRecord.data.fake_candidates = [];
        Ext.Array.each(record.data.candidates__student__username, function(username) {
            //editRecord.data.fake_candidates.push(devilry.administrator.studentsmanager.StudentsManagerManageGroups.parseCandidateSpec(candidateSpec));
            editRecord.data.fake_candidates.push({
                username: username,
                candidate_id: usernameToCandidateIdMap[username]
            });
        }, this);

        editRecord.save({
            scope: this,
            callback: function(records, operation) {
                // TODO: Show changes in success message!
                if(operation.success) {
                    this.progressWindow.addSuccess(record, 'Group successfully saved.');
                } else {
                    this.progressWindow.addErrorFromOperation(record, 'Failed to save changes to group.', operation);
                }

                this._finishedSavingGroupCount ++;
                if(this._finishedSavingGroupCount == totalSelectedGroups) {
                    this.loadFirstPage();
                    this.getEl().unmask();
                    this.progressWindow.finish();
                }
            }
        });
    },


    statics: {
        getCandidateInfoFromGroupRecord: function(record) {
            var candidates = [];
            Ext.each(record.data.candidates__student__username, function(username, index) {
                candidate = {username: username};
                if(record.data.parentnode__anonymous) {
                    candidate.candidate_id = record.data.candidates__identifier[index];
                }
                candidates.push(candidate);
            });
            return candidates;
        },

        formatCandidateInfoAsString: function(candidate) {
            if(candidate.candidate_id == undefined || candidate.candidate_id == "candidate-id missing") {
                return candidate.username;
            } else {
                return Ext.String.format('{0}:{1}', candidate.username, candidate.candidate_id);
            }
        },

        parseCandidateSpec: function(candidateSpec) {
            var asArray = candidateSpec.split(/\s*:\s*/);
            var candidate_id = asArray.length > 1? asArray[1]: null;
            return {
                username: asArray[0],
                candidate_id: candidate_id
            };
        },
    }
});
