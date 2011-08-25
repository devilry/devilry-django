/** The group management methods for StudentsManager. */
Ext.define('devilry.administrator.studentsmanager.StudentsManagerManageGroups', {
    requires: [
        'devilry.administrator.studentsmanager.ManuallyCreateUsers'
    ],

    /**
     * @private
     */
    showManuallyCreateUsersWindow: function(initialLines) {
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
                assignmentid: this.assignmentid,
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
    onManuallyCreateUsers: function() {
        this.showManuallyCreateUsersWindow();
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
        this.showManuallyCreateUsersWindow(this.relatedUserRecordsToArray(relatedStudents));
    },


    onChangeGroupName: function() {
        if(!this.singleSelected()) {
            this.onNotSingleSelected();
            return;
        }

        var me  = this;
        Ext.Msg.prompt('Change group name', 'Please enter a new group name:', function(btn, name){
            if (btn == 'ok'){
                var record = me.getSelection()[0];
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
        Ext.each(candidates, function(candidate, index) {
            if(candidate.candidate_id == undefined || candidate.candidate_id == "candidate-id missing") {
                candidatestrings.push(candidate.username);
            } else {
                candidatestrings.push(Ext.String.format('{0}:{1}', candidate.username, candidate.candidate_id));
            }
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
                    '<section class="helpsection">',
                    '   <tpl if="anonymous">',
                    '       <p>One candidate of on each line. Username and <em>candidate ID</em> is separated by a single colon. Note that <em>candidate ID</em> does not have to be a number.</p>',
                    '       <p>Example:</p>',
                    '       <pre style="padding: 5px;">bob:20\nalice:A753\neve:SEC-01\ndave:30</pre>',
                    '   </tpl>',
                    '   <tpl if="!anonymous">',
                    '       <p>One username on each line. Example</p>',
                    '       <pre style="padding: 5px;">bob\nalice\neve\ndave</pre>',
                    '   </tpl>',
                    '</section>'
                ),
                listeners: {
                    scope: this,
                    saveClicked: this.changeGroupMembers
                }
            },
        });
        win.show();
    },

    changeGroupMembers: function(setlistofusersobj, candidateSpecs) {
        var record = this.getSelection()[0];
        var editRecord = this.createRecordFromStoreRecord(record);
        editRecord.data.fake_candidates = [];
        Ext.Array.each(candidateSpecs, function(candidateSpec) {
            editRecord.data.fake_candidates.push(devilry.administrator.studentsmanager.StudentsManagerManageGroups.parseCandidateSpec(candidateSpec));
        }, this);

        setlistofusersobj.getEl().mask("Changing group members");
        editRecord.save({
            scope: this,
            failure: function() {
                setlistofusersobj.getEl().unmask();
                Ext.MessageBox.show({
                    title: 'Failed to change group members',
                    msg: 'This is normally caused by invalid usernames.',
                    buttons: Ext.Msg.OK,
                    icon: Ext.Msg.ERROR
                });
            },
            success: function() {
                setlistofusersobj.up('window').close();
                this.loadFirstPage();
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
