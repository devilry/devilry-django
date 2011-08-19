/** The examiner management methods for StudentsManager.
 *
 * Note that this class depends on the createRecordFromStoreRecord from
 * StudentsManager to be available. */
Ext.define('devilry.extjshelpers.studentsmanager.StudentsManagerManageExaminers', {
    
    /**
     * @private
     */
    onRandomDistributeExaminers: function() {
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
                usernames: ['donald', 'scrooge', 'daisy', 'clarabelle'],
                //usernames: [],
                helptext: '<p>The username of a single examiner on each line. Example:</p>',
                listeners: {
                    scope: this,
                    saveClicked: function(setlistofusersobj, usernames) {
                        this.randomDistributeExaminersOnSelected(setlistofusersobj, usernames);
                    }
                }
            },
        });
        win.show();
    },

    /**
     * @private
     */
    randomDistributeExaminersOnSelected: function(setlistofusersobj, examiners) {
        setlistofusersobj.up('window').close();

        this._randomDistributeTmp = {
            remainingExaminers: examiners,
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
    randomDistributeExaminers: function(record, index, totalSelectedGroups) {
        var msg = Ext.String.format('Random distributing examiner to group {0}/{1}', index, totalSelectedGroups);
        this.getEl().mask(msg);

        var editRecord = this.createRecordFromStoreRecord(record);
        var examiner = this.getRandomExaminer();
        this._randomDistributeTmp.result[examiner].push(editRecord);
        this.removeExaminerIfEnoughStudents(examiner, totalSelectedGroups);

        editRecord.data.fake_examiners = [examiner];
        editRecord.save({
            failure: function() {
                console.error('Failed to save record');
            }
        });

        if(index == totalSelectedGroups) {
            this.loadFirstPage();
            this.getEl().unmask();
            console.log(this._randomDistributeTmp.result);
        }
    },


    /**
     * @private
     */
    onSetExaminers: function(append) {
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
                //usernames: ['donald', 'scrooge'],
                usernames: [],
                helptext: '<p>The username of a single examiner on each line. Example:</p>',
                listeners: {
                    scope: this,
                    saveClicked: function(setlistofusersobj, usernames) {
                        this.setExaminersOnSelected(setlistofusersobj, usernames, append);
                    }
                }
            },
        });
        win.show();
    },


    /**
     * @private
     */
    onAddExaminers: function() {
        console.log('TP');
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
            failure: function() {
                console.error('Failed to save record');
            }
        });

        if(index == totalSelectedGroups) {
            this.loadFirstPage();
            this.getEl().unmask();
        }
    }
});
