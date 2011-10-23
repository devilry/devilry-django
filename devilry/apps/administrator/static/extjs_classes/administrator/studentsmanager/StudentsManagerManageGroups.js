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
        var format = '{user__username}';
        if(this.assignmentrecord.data.anonymous) {
            format += '<tpl if="candidate_id">:{candidate_id}</tpl>'
        }
        format += '<tpl if="tags"> ({tags})</tpl>';
        var userspecs = this.relatedUserRecordsToStringArray(relatedStudents, format);
        this.createManyGroupsInBulk(userspecs);
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
            title: 'Import candidate IDs',
            modal: true,
            width: 800,
            height: 600,
            maximizable: true,
            layout: 'fit',
            items: {
                xtype: 'setlistofusers',
                usernames: [],
                fieldLabel: 'Candidates',
                anonymous: this.assignmentrecord.anonymous,
                helptpl: Ext.create('Ext.XTemplate',
                    '<div class="section helpsection">',
                    '    <p><strong>Warning:</strong> This action will replace/clear candidate IDs on every selected group.</p>',
                    '    <p>The <em>intended use case</em> for this window is to paste candidate IDs into Devilry instead of setting candidate IDs manually.</p>',
                    '    <p>The format is one candidate on each line. Username and <em>candidate ID</em> is separated by whitespace and/or a single colon, comma or semicolon. Note that <em>candidate ID</em> does not have to be a number.</p>',
                    '    <p><strong>Example</strong> (using colon to separate username and candidate ID):</p>',
                    '    <pre style="padding: 5px;">bob:20\nalice:A753\neve:SEC-01\ndave:30</pre>',
                    '    <p><strong>Example</strong> (showing all of the supported separators):</p>',
                    '    <pre style="padding: 5px;">bob    20\nalice : A753\neve, SEC-01\ndave;  30</pre>',
                    '</div>'
                ),
                listeners: {
                    scope: this,
                    saveClicked: function(setlistofusersobj, candidateSpecs, caller) {
                        try {
                            var usernameToCandidateIdMap = this.parseCandidateImportFormat(candidateSpecs);
                        } catch(e) {
                            Ext.MessageBox.alert('Error', e);
                            return;
                        }
                        setlistofusersobj.up('window').close();
                        this.progressWindow.start('Set candidate ID on many');
                        this._finishedSavingGroupCount = 0;
                        this.down('studentsmanager_studentsgrid').performActionOnSelected({
                            scope: this,
                            callback: this.setCandidateId,
                            extraArgs: [usernameToCandidateIdMap]
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
            var s = candidateSpec.split(/\s*[:,;\s]\s*/);
            if(candidateSpec.length > 0) {
                if(s.length != 2) {
                    throw Ext.String.format('Invalid format on line {0}: {1}', index, candidateSpec)
                }
                usernameToCandidateIdMap[s[0]] = s[1];
            }
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
        editRecord.data.fake_candidates = [];

        var result_preview = '';
        var usernames = record.data.candidates__student__username;
        Ext.Array.each(usernames, function(username, index) {
            var candidate_id = usernameToCandidateIdMap[username];
            editRecord.data.fake_candidates.push({
                username: username,
                candidate_id: candidate_id
            });
            result_preview += username;
            if(candidate_id) {
                result_preview += username + ':';
            } else {
                this.progressWindow.addWarning(record, Ext.String.format('No Candidate ID for {0}.', username));
            }
            if(index < usernames.length) {
                result_preview += ', ';
            }
        }, this);

        editRecord.save({
            scope: this,
            callback: function(records, operation) {
                if(operation.success) {
                    this.progressWindow.addSuccess(record, Ext.String.format('Candidate IDs successfully updated to: {0}.', result_preview));
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
