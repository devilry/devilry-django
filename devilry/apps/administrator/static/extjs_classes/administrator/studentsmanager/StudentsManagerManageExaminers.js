/** The examiner management methods for StudentsManager.
 *
 * Note that this class depends on createRecordFromStoreRecord(),
 * onSelectNone() and loadFirstPage() from StudentsManager to be available. */
Ext.define('devilry.administrator.studentsmanager.StudentsManagerManageExaminers', {
    depends: [
        'devilry.administrator.studentsmanager.ManuallyCreateUsers',
        'devilry.extjshelpers.EvenRandomSelection'
    ],

    randomDistResultTpl: Ext.create('Ext.XTemplate',
        '<div class="section info">',
        '    <p>The selected examiners got the following number of groups:</p>',
        '    <ul>',
        '    <tpl for="result">',
        '       <li><strong>{examiner}</strong>: {groups.length}</li>',
        '    </tpl>',
        '    </ul>',
        '</div>'
    ),

    successSetExaminerTpl: Ext.create('Ext.XTemplate',
        'Examiners set successfully to: <tpl for="examiners">',
        '   {.}<tpl if="xindex &lt; xcount">, </tpl>',
        '</tpl>'
    ),

    errorSetExaminerTpl: Ext.create('Ext.XTemplate',
        'Failed to set examiners: <tpl for="examiners">',
        '   {.}<tpl if="xindex &lt; xcount">, </tpl>',
        '</tpl>. Error details: {errorDetails}'
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

        var randomDistResult = [];
        Ext.each(examiners, function(examiner, index) {
            randomDistResult[examiner] = [];
        }, this);

        var randomExaminerPool = Ext.create('devilry.extjshelpers.EvenRandomSelection', {
            selection: examiners
        })

        this.down('studentsmanager_studentsgrid').performActionOnSelected({
            scope: this,
            callback: this.randomDistributeExaminers,
            extraArgs: [randomExaminerPool, randomDistResult]
        });
    },

    /**
     * @private
     */
    getRandomDistributeResults: function(allExaminers, randomDistResult) {
        var resultArray = [];
        Ext.each(allExaminers, function(examiner, index) {
            resultArray.push({
                examiner: examiner,
                groups: randomDistResult[examiner]
            });
        }, this);
        return this.randomDistResultTpl.apply({result: resultArray});
    },


    /**
     * @private
     */
    randomDistributeExaminers: function(record, index, totalSelectedGroups, randomExaminerPool, randomDistResult) {
        var msg = Ext.String.format('Random distributing examiner to group {0}/{1}', index, totalSelectedGroups);
        this.getEl().mask(msg);

        var editRecord = this.createRecordFromStoreRecord(record);
        var examiner = randomExaminerPool.getRandomItem();
        randomDistResult[examiner].push(editRecord);

        editRecord.data.fake_examiners = [examiner];
        editRecord.save({
            scope: this,
            callback: function(r, operation) {
                this.setExaminerRecordCallback(record, operation, [examiner], totalSelectedGroups);
                if(this._finishedSavingGroupCount == totalSelectedGroups) {
                    this.progressWindow.finish({
                        title: 'Result of random distribution of examiners',
                        html: this.getRandomDistributeResults(randomExaminerPool.selection, randomDistResult)
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
        var usernames = [];
        Ext.each(relatedExaminers, function(relatedExaminer, index) {
            usernames.push(relatedExaminer.get('user__username'));
        }, this);
        setlistofusersobj.setValueFromArray(usernames);
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
            usernames = Ext.Array.merge(usernames, record.data.examiners__user__username);
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
                errorDetails: devilry.extjshelpers.RestProxy.formatHtmlErrorMessage(operation)
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
                help: '<div class="section helpsection">Select the assignment you wish to import examiners from. When you click next, every selected assignemnt group in the current assignment with <strong>exactly</strong> the same members as in the selected assignment, will have their examiners copied into the current assignment.</div>',
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
    },


    onSetExaminersFromTags: function() {
        if(this.noneSelected()) {
            this.onSelectNone();
            return;
        }
        this.loadAllRelatedExaminers({
            scope: this,
            callback: this.setExaminersFromTags
        });
    },

    setExaminersFromTags: function(relatedExaminers) {
        this.progressWindow.start('Match tagged examiners to equally tagged groups');
        this._finishedSavingGroupCount = 0;
        this.down('studentsmanager_studentsgrid').performActionOnSelected({
            scope: this,
            callback: this.setExaminersFromTagsOnSingleGroup,
            extraArgs: [relatedExaminers]
        });
    },

    setExaminersFromTagsOnSingleGroup: function(groupRecord, index, totalSelectedGroups, relatedExaminers) {
        var msg = Ext.String.format('Setting examiners on group {0}/{1}', index, totalSelectedGroups);
        this.getEl().mask(msg);

        var editRecord = this.createRecordFromStoreRecord(groupRecord);
        var matchedExaminerUsernames = this.examinersMatchesGroupTags(groupRecord, relatedExaminers);

        editRecord.data.fake_examiners = matchedExaminerUsernames;
        editRecord.save({
            scope: this,
            callback: function(r, operation) {
                this.setExaminerRecordCallback(groupRecord, operation, matchedExaminerUsernames, totalSelectedGroups);
                if(this._finishedSavingGroupCount == totalSelectedGroups) {
                    this.progressWindow.finish();
                }
            }
        });
    },

    examinersMatchesGroupTags: function(groupRecord, relatedExaminers) {
        var matchedExaminerUsernames = [];
        Ext.each(relatedExaminers, function(relatedExaminer, index) {
            var tagsString = relatedExaminer.get('tags');
            if(tagsString) {
                var tags = tagsString.split(',');
                //console.log(relatedExaminer.get('user__username'), tags);
                var intersect = Ext.Array.intersect(groupRecord.data.tags__tag, tags);
                if(intersect.length > 0) {
                    Ext.Array.include(matchedExaminerUsernames, relatedExaminer.get('user__username'));
                }
            }
        });
        return matchedExaminerUsernames;
    }
});
