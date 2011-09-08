/** The examiner management methods for StudentsManager.
 *
 * Note that this class depends on createRecordFromStoreRecord(),
 * onSelectNone() and loadFirstPage() from StudentsManager to be available. */
Ext.define('devilry.administrator.studentsmanager.StudentsManagerManageExaminers', {

    randomDistResultTpl: Ext.create('Ext.XTemplate',
        '<section class="info">',
        '    <p>The selected examiners got the following number of groups:</p>',
        '    <ul>',
        '    <tpl for="result">',
        '       <li><strong>{examiner}</strong>: {groups.length}</li>',
        '    </tpl>',
        '    </ul>',
        '</section>'
    ),

    successSetExaminerTpl: Ext.create('Ext.XTemplate',
        'Examiners set successfully to: <tpl for="examiners">',
        '   {.}<tpl if="xindex &lt; xcount">, </tpl>',
        '</tpl>'
    ),

    errorSetExaminerTpl: Ext.create('Ext.XTemplate',
        'Failed to set examiners: <tpl for="examiners">',
        '   {.}<tpl if="xindex &lt; xcount">, </tpl>',
        '</tpl>. Error details:',
        '<tpl if="status === 403">',
        '   {status} {statusText}. This is ususall caused by an <strong>invalid username</strong>.',
        '</tpl>',
        '<tpl if="status !== 403">',
        '   <tpl if="status === 0">',
        '       Could not contact the Devilry server.',
        '   </tpl>',
        '   <tpl if="status !== 0">',
        '       {status} {statusText}.',
        '   </tpl>',
        '</tpl>'
    ),
    
    /**
     * @private
     */
    onRandomDistributeExaminers: function() {
        //this.down('studentsmanager_studentsgrid').selModel.selectAll();
        if(this.noneSelected()) {
            this.onSelectNone();
            return;
        }
        var win = Ext.widget('window', {
            title: 'Select examiners',
            modal: true,
            width: 500,
            height: 400,
            maximizable: true,
            layout: 'fit',
            items: {
                xtype: 'setlistofusers',
                //usernames: ['donald', 'scrooge', 'daisy', 'clarabelle'],
                usernames: [],
                helptext: '<p>The username of a single examiner on each line. Example:</p>',
                listeners: {
                    scope: this,
                    saveClicked: function(setlistofusersobj, usernames) {
                        this.randomDistributeExaminersOnSelected(setlistofusersobj, usernames);
                    }
                },

                extraToolbarButtons: [{
                    xtype: 'button',
                    scale: 'large',
                    text: Ext.String.format('Import examiners registered in {0}', DevilrySettings.DEVILRY_SYNCSYSTEM),
                    listeners: {
                        scope: this,
                        click: this.onImportRelatedExaminers
                    }
                }]
            }
        });
        win.show();
    },

    /**
     * @private
     */
    randomDistributeExaminersOnSelected: function(setlistofusersobj, examiners) {
        setlistofusersobj.up('window').close();
        this.progressWindow.start('Change examiners');
        this._finishedSavingGroupCount = 0;

        this._randomDistributeTmp = {
            remainingExaminers: Ext.Array.clone(examiners),
            allExaminers: examiners,
            totExaminers: examiners.length,
            result: {}
        };
        Ext.each(examiners, function(examiner, index) {
            this._randomDistributeTmp.result[examiner] = [];
        }, this);

        this.down('studentsmanager_studentsgrid').performActionOnSelected({
            scope: this,
            callback: this.randomDistributeExaminers,
            extraArgs: []
        });
    },

    /**
     * @private
     */
    getRandomExaminer: function() {
        var numRemainingExaminers = this._randomDistributeTmp.remainingExaminers.length;
        var randomIndex = Math.floor(Math.random() * (numRemainingExaminers));
        return this._randomDistributeTmp.remainingExaminers[randomIndex];
    },

    /**
     * @private
     */
    removeExaminerIfEnoughStudents: function(examiner, totalSelectedGroups) {
        var totExaminers = this._randomDistributeTmp.totExaminers;
        var groupsPerExaminer = Math.ceil(totalSelectedGroups/totExaminers);
        if(this._randomDistributeTmp.result[examiner].length === groupsPerExaminer) {
            Ext.Array.remove(this._randomDistributeTmp.remainingExaminers, examiner);
        }
    },

    /**
     * @private
     */
    getRandomDistributeResults: function() {
        var resultArray = [];
        Ext.each(this._randomDistributeTmp.allExaminers, function(examiner, index) {
            resultArray.push({
                examiner: examiner,
                groups: this._randomDistributeTmp.result[examiner]
            });
        }, this);
        return this.randomDistResultTpl.apply({result: resultArray});
    },


    /**
     * @private
     */
    randomDistributeExaminers: function(record, index, totalSelectedGroups) {
        var msg = Ext.String.format('Random distributing examiner to group {0}/{1}', index, totalSelectedGroups);
        this.getEl().mask(msg);

        var editRecord = this.createRecordFromStoreRecord(record);
        var examiner = this.getRandomExaminer();
        this._randomDistributeTmp.result[examiner].push(editRecord);
        this.removeExaminerIfEnoughStudents(examiner, totalSelectedGroups);

        editRecord.data.fake_examiners = [examiner];
        editRecord.save({
            scope: this,
            callback: function(r, operation) {
                this.setExaminerRecordCallback(record, operation, [examiner], totalSelectedGroups);
                if(this._finishedSavingGroupCount == totalSelectedGroups) {
                    this.progressWindow.finish({
                        title: 'Result of random distribution of examiners',
                        html: this.getRandomDistributeResults()
                    });
                }
            }
        });
    },


    /**
     * @private
     */
    onSetExaminers: function(append) {
        //this.down('studentsmanager_studentsgrid').selModel.selectAll();
        if(this.noneSelected()) {
            this.onSelectNone();
            return;
        }
        var helptext = '<p>The username of a single examiner on each line.' +
            (append? '': '<strong> Current examiners will be replaced</strong>.') +
            '</p><p>Example:</p>';
        var win = Ext.widget('window', {
            title: (append? 'Add examiners': 'Replace examiners') + ' - select examiners',
            modal: true,
            width: 500,
            height: 400,
            maximizable: true,
            layout: 'fit',
            items: {
                xtype: 'setlistofusers',
                //usernames: ['donald', 'scrooge'],
                usernames: [],
                helptext: helptext,
                listeners: {
                    scope: this,
                    saveClicked: function(setlistofusersobj, usernames) {
                        this.setExaminersOnSelected(setlistofusersobj, usernames, append);
                    }
                },

                extraToolbarButtons: [{
                    xtype: 'button',
                    scale: 'large',
                    text: Ext.String.format('Import examiners registered in {0}', DevilrySettings.DEVILRY_SYNCSYSTEM),
                    listeners: {
                        scope: this,
                        click: this.onImportRelatedExaminers
                    }
                }]
            },
        });
        win.show();
    },

    onImportRelatedExaminers: function(button) {
        var setlistofusersobj = button.up('setlistofusers');
        this.loadAllRelatedExaminers({
            scope: this,
            callback: this.importRelatedExaminers,
            args: [setlistofusersobj]
        });
    },

    importRelatedExaminers: function(relatedExaminers, setlistofusersobj) {
        var examiners = this.relatedUserRecordsToArray(relatedExaminers);
        setlistofusersobj.setValueFromArray(examiners);
    },


    /**
     * @private
     */
    onAddExaminers: function() {
        this.onSetExaminers(true);
    },

    /**
     * @private
     */
    onReplaceExaminers: function() {
        this.onSetExaminers(false);
    },

    /**
     * @private
     */
    onClearExaminers: function() {
        if(this.noneSelected()) {
            this.onSelectNone();
            return;
        }

        this.progressWindow.start('Clear examiners');
        this._finishedSavingGroupCount = 0;
        Ext.MessageBox.show({
            title: 'Confirm clear examiners?',
            msg: 'Are you sure you want to clear examiners on all the selected groups?',
            buttons: Ext.Msg.YESNO,
            icon: Ext.Msg.WARNING,
            scope: this,
            fn: function(btn) {
                if(btn == 'yes') {
                    this.down('studentsmanager_studentsgrid').performActionOnSelected({
                        scope: this,
                        callback: this.setExaminers,
                        extraArgs: [[], false]
                    });
                }
            }
        });
    },


    /**
     * @private
     */
    setExaminersOnSelected: function(setlistofusersobj, usernames, append) {
        setlistofusersobj.up('window').close();
        this.progressWindow.start('Change examiners');
        this._finishedSavingGroupCount = 0;
        this.down('studentsmanager_studentsgrid').performActionOnSelected({
            scope: this,
            callback: this.setExaminers,
            extraArgs: [usernames, append]
        });
    },


    /**
     * @private
     */
    setExaminers: function(record, index, totalSelectedGroups, usernames, append) {
        var msg = Ext.String.format('Setting examiners on group {0}/{1}', index, totalSelectedGroups);
        this.getEl().mask(msg);

        if(append) {
            usernames = Ext.Array.merge(usernames, record.data.examiners__username);
        };

        var editRecord = this.createRecordFromStoreRecord(record);
        editRecord.data.fake_examiners = usernames;
        editRecord.save({
            scope: this,
            callback: function(r, operation) {
                this.setExaminerRecordCallback(record, operation, usernames, totalSelectedGroups);
                if(this._finishedSavingGroupCount == totalSelectedGroups) {
                    this.progressWindow.finish();
                }
            }
        });
    },

    /**
     * @private
     */
    setExaminerRecordCallback: function(record, operation, usernames, totalSelectedGroups) {
        if(operation.success) {
            var msg = this.successSetExaminerTpl.apply({
                examiners: usernames
            });
            this.progressWindow.addSuccess(record, msg);
        } else {
            var msg = this.errorSetExaminerTpl.apply({
                examiners: usernames,
                status: operation.error.status,
                statusText: operation.error.statusText
            });
            this.progressWindow.addError(record, msg);
        }

        this._finishedSavingGroupCount ++;
        if(this._finishedSavingGroupCount == totalSelectedGroups) {
            this.loadFirstPage();
            this.getEl().unmask();
        }
    },


    onImportExaminersFromAnotherAssignmentInCurrentPeriod: function() {
        //this.down('studentsmanager_studentsgrid').selModel.selectAll();
        if(this.noneSelected()) {
            this.onSelectNone();
            return;
        }
        Ext.widget('window', {
            title: 'Import examiners from another assignment in the current Period',
            layout: 'fit',
            width: 830,
            height: 600,
            modal: true,
            items: {
                xtype: 'importgroupsfromanotherassignment',
                periodid: this.periodid,
                help: '<section class="helpsection">Select the assignment you wish to import examiners from. When you click next, every selected assignemnt group in the current assignment with <strong>exactly</strong> the same members as in the selected assignment, will have their examiners copied into the current assignment.</section>',
                listeners: {
                    scope: this,
                    next: this.importExaminersFromAnotherAssignmentInCurrentPeriod
                }
            }
        }).show();
    },

    /**
     * @private
     */
    importExaminersFromAnotherAssignmentInCurrentPeriod: function(importPanel, otherGroupRecords) {
        importPanel.up('window').close();
        this.progressWindow.start('Copy examiners from another assignment');
        this.down('studentsmanager_studentsgrid').gatherSelectedRecordsInArray({
            scope: this,
            callback: function(currentGroupRecords) {
                var matchingRecordPairs = this.findGroupsWithSameStudents(currentGroupRecords, otherGroupRecords);
                this.copyExaminersFromOtherGroups(matchingRecordPairs);
            }
        });
    },

    findGroupsWithSameStudents: function(currentGroupRecords, otherGroupRecords) {
        var matchingRecordPairs = [];
        Ext.each(currentGroupRecords, function(currentRecord, index) {
            var currentUsernames = currentRecord.data.candidates__student__username;
            var matchFound = false;
            this.getEl().mask(Ext.String.format('Finding groups with the same students {0}/{1}...', index, currentGroupRecords.length));
            Ext.each(otherGroupRecords, function(otherRecord, index) {
                var otherUsernames = otherRecord.data.candidates__student__username;
                if(currentUsernames.length === otherUsernames.length) {
                    var difference = Ext.Array.difference(currentUsernames, otherUsernames);
                    if(difference.length === 0) {
                        //console.log(otherUsernames, '===', currentUsernames);
                        matchingRecordPairs.push({
                            current: currentRecord,
                            other: otherRecord
                        });
                        matchFound = true;
                        return false; // break
                    }
                }
            }, this);
            if(!matchFound) {
                this.progressWindow.addWarning(currentRecord, 'Group not found in the other assignment.');
            }
        }, this);
        return matchingRecordPairs;
    },


    copyExaminersFromOtherGroups: function(matchingRecordPairs) {
        this._finishedSavingGroupCount = 0;
        Ext.each(matchingRecordPairs, function(recordPair, index) {
            this.setExaminers(recordPair.current, index, matchingRecordPairs.length, recordPair.other.data.examiners__username, false);
        }, this);
    }
});
