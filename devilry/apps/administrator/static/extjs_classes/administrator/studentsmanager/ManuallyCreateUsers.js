Ext.define('devilry.administrator.studentsmanager.ManuallyCreateUsers', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.manuallycreateusers',
    frame: false,
    border: false,
    poolSize: 20,

    requires: [
        'devilry.extjshelpers.AsyncActionPool'
    ],

    layout: {
        type: 'vbox',
        align: 'stretch' // Child items are stretched to full width
    },

    config: {
        /**
         * @cfg
         * Lines to fill in on load (one line for each element in the array).
         */
        initialLines: undefined,

        currentGroupRecords: undefined,
        assignmentrecord: undefined,
        deadlinemodel: undefined,
        suggestedDeadline: undefined
    },

    helptext:
        '<div class="section helpsection">' +
        //'   <h1>Help</h1>' +
        '   <p>Students are organized in <em>assignment groups</em>. You should specify <strong>one</strong> <em>assignment group</em> on each line in the input box.</p>' +
        '   <p>Check <strong>Ignore duplicates</strong> to ignore any assignment groups that contains students that already has an assignment group on this assignment.</p>' +
        '   <h2>Common usage examples</h2>' +
        '   <h3>Individual deliveries</h3>' +
        '   <p>Very often, an assignment requires <strong>individual</strong> deliveries and feedback. In this case, each <em>assignment group</em> should contain a single student. In this case, the input box should contain something similar to this:</p>' +
        '   <pre style="margin-left:30px; border: 1px solid #999; padding: 5px;">bob\nalice\neve\ndave</pre>' +

        '   <h3>Group deliveries</h3>' +
        '   <p>When students are supposed to <strong>cooperate</strong> on the same assignment, they should be in the same <em>assignment group</em>. In this case, the input box should contain something similar to this:</p>' +
        '   <pre style="margin-left:30px; border: 1px solid #999; padding: 5px;">bob, alice\neve, dave, charlie</pre>' +

        '   <h3>Anonymous assignments</h3>' +
        '   <p>When you have specified the the assignment is anonymous, you may want to give each student a <em>candidate-id</em> that the examiners will see instead of the username. Specify candidate-id with a colon at the end of each username like this:</p>' +
        '   <pre style="margin-left:30px; border: 1px solid #999; padding: 5px;">bob:10, alice:232\ncharlie:4X23</pre>' +

        '   <h3>Project groups and group naming</h3>' +
        '   <p>It is often useful to give an <em>assignment group</em> a <strong>name</strong>. The name is primarily intended for project assignments, where it is useful to name a group after their project. However, the name can be used for other purposes, such as <em>tagging</em> of groups of special interest. Since you can search for groups by name, you can name multiple groups with tags, such as <em>exceptional</em>, and find these groups using the search field. You specify group name like this:</p>' +
        '   <pre style="margin-left:30px; border: 1px solid #999; padding: 5px;">Secret project:: bob, alice\nTake over world:: eve, dave, charlie</pre>' +

        '   <h2>Input format explained in detail</h2>' +
        '   <p>The format used to create the assignment groups is:</p>' +
        '   <ul>' +
        '       <li>One assignment group on each line.</li>' +
        '       <li>Each username is separated by a comma.</li>' +
        '       <li>Group name is identified by two colons at the end of the name, and must be placed at the beginning of the line.</li>' +
        '       <li>A group name or at least one username is required for each group.</li>' +
        '       <li>An optional <em>candidate-id</em> for a candidate is denoted by a colon and the <em>candidate-id</em> after the username.</li>' +
        '       <li>A an optional comma-separated list of tags surrounded by parentheses.</li>' +
        '   </ul>' +
        '</div>',

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },

    initComponent: function() {
        this.assignmentGroupModelCls = 'devilry.apps.administrator.simplified.SimplifiedAssignmentGroup';

        var currentValue = "";
        if(this.initialLines) {
            Ext.each(this.initialLines, function(line, index) {
                currentValue += Ext.String.format('{0}\n', line);
            });
        };

        this.userinput = Ext.widget('textareafield', {
            //hideLabel: true,
            fieldLabel: 'Assignment groups',
            labelAlign: 'top',
            labelWidth: 100,
            labelStyle: 'font-weight:bold',
            emptyText: 'Read the text on your right hand side for help...',
            flex: 10,
            value: currentValue
        });

        this.clearDupsCheck = Ext.widget('checkbox', {
            boxLabel: "Ignore duplicates?",
            checked: true
        });
        //this.userinput.setValue('dewey\nlouie:401, hue\n\nSaker azz:: donald, dela:30');
        //this.userinput.setValue('dewey\nlouie:401');
        Ext.apply(this, {
            //items: this.userinput,

            layout: {
                type: 'hbox',
                align: 'stretch'
            },

            items: [{
                margin: 10,
                flex: 10,
                xtype: 'panel',
                border: false,
                layout: {
                    type: 'vbox',
                    align: 'stretch'
                },
                items: [this.userinput, this.clearDupsCheck],
            }, {
                flex: 10,
                xtype: 'box',
                padding: 20,
                autoScroll: true,
                html: this.helptext
            }],

            dockedItems: [{
                xtype: 'toolbar',
                dock: 'bottom',
                ui: 'footer',
                items: ['->', {
                    xtype: 'button',
                    iconCls: 'icon-next-32',
                    scale: 'large',
                    text: 'Select deadline',
                    listeners: {
                        scope: this,
                        click: this.onCreate
                    }
                }]
            }]
        });
        this.callParent(arguments);
    },

    /**
     * @private
     */
    parseGroupSpec: function(groupSpec) {
        groupSpec = Ext.String.trim(groupSpec);
        if(groupSpec == "") {
            return null;
        }
        groupSpecObj = {
            name: null,
            is_open: true,
            fake_candidates: [],
            fake_examiners: [],
            fake_tags: []
        };

        var nameSplit = groupSpec.split(/\s*::\s*/);
        if(nameSplit.length > 1) {
            groupSpecObj.name = nameSplit[0];
            groupSpec = nameSplit[1];
        }

        var usernamesAndTags = this.statics().parseUsernamesAndTags(groupSpec);
        groupSpecObj.fake_tags = usernamesAndTags.tags;

        Ext.Array.each(usernamesAndTags.usernames, function(candidateSpec) {
            groupSpecObj.fake_candidates.push(devilry.administrator.studentsmanager.StudentsManagerManageGroups.parseCandidateSpec(candidateSpec));
        }, this);
        return groupSpecObj;
    },

    /**
     * @private
     */
    parseTextToGroupSpec: function(rawValue) {
        var asArray = rawValue.split('\n');
        var resultArray = [];
        var me = this;
        Ext.Array.each(asArray, function(groupSpec) {
            var groupSpecObj = me.parseGroupSpec(groupSpec);
            if(groupSpecObj != null) {
                resultArray.push(groupSpecObj);
            }
        });
        return resultArray;
    },

    /**
     * @private
     */
    createAll: function(parsedArray) {
        this.getEl().mask(Ext.String.format('Saving {0} groups', parsedArray.length));
        this.finishedCounter = 0;
        this.unsuccessful = [];
        this.parsedArray = parsedArray;
        Ext.Array.each(this.parsedArray, function(groupSpecObj) {
            this.createGroup(groupSpecObj);
        }, this);
    },

    /**
     * @private
     */
    clearDuplicates: function(parsedArray) {
        var current_usernames = []
        Ext.each(this.currentGroupRecords, function(groupRecord) {
            var group_usernames = groupRecord.data.candidates__student__username;
            current_usernames = Ext.Array.merge(current_usernames, group_usernames);
        });

        var uniqueGroupSpecObjs = [];
        var new_usernames = [];
        Ext.Array.each(parsedArray, function(groupSpecObj) {
            var dups = false;
            Ext.Array.each(groupSpecObj.fake_candidates, function(candidate) {
                if(Ext.Array.contains(current_usernames, candidate.username) || Ext.Array.contains(new_usernames, candidate.username)) {
                    dups = true;
                }
            }, this);
            if(!dups) {
                Ext.Array.each(groupSpecObj.fake_candidates, function(candidate) {
                    new_usernames.push(candidate.username);
                });
                uniqueGroupSpecObjs.push(groupSpecObj);
            }
        }, this);

        return uniqueGroupSpecObjs;
    },


    _createGroupCallback: function(pool, groupSpecObj) {
        var completeGroupSpecObj = {
            parentnode: this.assignmentrecord.data.id
        };
        Ext.apply(completeGroupSpecObj, groupSpecObj);
        var group = Ext.create(this.assignmentGroupModelCls, completeGroupSpecObj);
        group.save({
            scope: this,
            callback: function(records, op) {
                pool.notifyTaskCompleted();
                if(op.success) {
                    this.createDeadline(records);
                } else {
                    this.finishedCounter ++;
                    this.unsuccessful.push(groupSpecObj);
                    this.getEl().mask(
                        Ext.String.format('Finished saving {0}/{1} groups',
                            this.finishedCounter, this.parsedArray.length, this.parsedArray.length
                        )
                    );
                    if(this.finishedCounter == this.parsedArray.length) {
                        this.onFinishedSavingAll();
                    }
                }
            }
        });
    },

    /**
     * @private
     */
    createGroup: function(groupSpecObj) {
        devilry.extjshelpers.AsyncActionPool.add({
            scope: this,
            args: [groupSpecObj],
            callback: this._createGroupCallback
        });
    },

    _createDeadlineCallback: function(pool, assignmentGroupRecord) {
        devilry.extjshelpers.studentsmanager.StudentsManagerManageDeadlines.createDeadline(
            assignmentGroupRecord, this.deadlineRecord, this.deadlinemodel, {
                scope: this,
                failure: function() {
                    console.error('Failed to save deadline record');
                },
                success: this.onCreateDeadlineSuccess
            }
        );
    },

    /**
     * @private
     */
    createDeadline: function(assignmentGroupRecord) {
        devilry.extjshelpers.AsyncActionPool.add({
            scope: this,
            args: [assignmentGroupRecord],
            callback: this._createDeadlineCallback
        });
    },

    /**
     * @private
     */
    onCreateDeadlineSuccess: function(record) {
        this.finishedCounter ++;
        this.getEl().mask(Ext.String.format('Finished saving {0}/{1} groups',
            this.finishedCounter, this.parsedArray.length,
            this.parsedArray.length
        ));
        if(this.finishedCounter == this.parsedArray.length) {
            this.onFinishedSavingAll();
        }
    },

    /**
     * @private
     */
    groupSpecObjToString: function(groupSpecObj) {
        var groupSpecStr = "";
        if(groupSpecObj.name) {
            groupSpecStr += groupSpecObj.name + ":: ";
        }
        Ext.Array.each(groupSpecObj.fake_candidates, function(candidate, index) {
            groupSpecStr += candidate.username;
            if(candidate.candidate_id) {
                groupSpecStr += ':' + candidate.candidate_id;
            }
            if(index != groupSpecObj.fake_candidates.length-1) {
                groupSpecStr += ', ';
            }
        }, this);
        return groupSpecStr;
    },

    /**
     * @private
     */
    groupSpecObjArrayToString: function(groupSpecObjArray) {
        var str = "";
        Ext.Array.each(groupSpecObjArray, function(groupSpecObj) {
            str += this.groupSpecObjToString(groupSpecObj) + '\n';
        }, this);
        return str;
    },

    /**
     * @private
     */
    onFinishedSavingAll: function() {
        this.getEl().unmask();
        if(this.unsuccessful.length == 0) {
            this.onSuccess();
        } else {
            this.onFailure();
        }
    },

    /**
     * @private
     */
    onSuccess: function() {
        var me = this;
        Ext.MessageBox.show({
            title: 'Success',
            msg: Ext.String.format('Created {0} assignment groups.', this.finishedCounter),
            buttons: Ext.Msg.OK,
            icon: Ext.Msg.INFO,
            fn: function() {
                me.userinput.setValue('');
                me.up('window').close();
            }
        });
    },

    /**
     * @private
     */
    onFailure: function() {
        this.userinput.setValue(this.groupSpecObjArrayToString(this.unsuccessful));
        Ext.MessageBox.show({
            title: 'Error',
            msg: Ext.String.format(
                'Failed to create {0} of {1} assignment groups. This is usually caused by invalid usernames. The groups with errors have been re-added to the input box.',
                this.unsuccessful.length, this.finishedCounter),
            buttons: Ext.Msg.OK,
            icon: Ext.Msg.ERROR
        });
    },

    /**
     * @private
     */
    onCreate: function() {
        this.getEl().mask('Parsing input');
        var parsedArray = this.parseTextToGroupSpec(this.userinput.getValue());
        this.getEl().unmask();
        var clearDuplicates = this.clearDupsCheck.getValue();
        if(clearDuplicates) {
            cleanedParsedArray = this.clearDuplicates(parsedArray);
            var diff = Ext.Array.difference(parsedArray, cleanedParsedArray);
            var me = this;
            if(diff.length > 0) {
                this.showClearedDuplicatesInfoWindow(cleanedParsedArray, diff);
            } else {
                this.checkForNoGroups(parsedArray);
            }
        } else {
            this.checkForNoGroups(parsedArray);
        }
    },

    /**
     * @private
     */
    showClearedDuplicatesInfoWindow: function(cleanedParsedArray, diff) {
        var me = this;
        var msg = Ext.create('Ext.XTemplate',
            '<div class="section helpsection">',
            '<p>The groups listed below contains at least one student that already has a group on this assignment. If you choose <em>Next</em>, these groups will be ignored. Choose <em>Cancel</em> to return to the <em>Create assignment groups</em> window.</p>',
            '<ul>',
            '   <tpl for="diff"><li>',
            '       <tpl if="name">',
            '           {name}:: ',
            '       </tpl>',
            '       <tpl for="fake_candidates">',
            '           {username}<tpl if="candidate_id">{candidate_id}</tpl><tpl if="xindex &lt; xcount">, </tpl>',
            '       </tpl>',
            '       <tpl if="fake_tags.length &gt; 0">',
            '          (<tpl for="fake_tags">',
            '              {.}<tpl if="xindex &lt; xcount">, </tpl>',
            '          </tpl>)',
            '       </tpl>',
            '   </tpl></li>',
            '</ul></div>'
        ).apply({diff: diff});
        Ext.widget('window', {
            width: 500,
            height: 400,
            modal: true,
            title: 'Confirm clear duplicates',
            layout: 'fit',
            items: {
                xtype: 'panel',
                border: false,
                html: msg
            },
            dockedItems: [{
                xtype: 'toolbar',
                dock: 'bottom',
                ui: 'footer',
                items: [{
                    xtype: 'button',
                    scale: 'large',
                    text: 'Cancel',
                    listeners: {
                        click: function() {
                            this.up('window').close();
                        }
                    }
                }, '->', {
                    xtype: 'button',
                    iconCls: 'icon-next-32',
                    scale: 'large',
                    text: 'Next',
                    listeners: {
                        click: function() {
                            this.up('window').close();
                            me.checkForNoGroups(cleanedParsedArray, 'No groups where created because all groups contained students that already have a group, and you chose to ignore duplicates.');
                        }
                    }
                }]
            }]
        }).show();
    },

    /**
     * @private
     */
    checkForNoGroups: function(parsedArray, noGroupsMsg) {
        if(parsedArray.length == 0) {
            var msg = noGroupsMsg || 'You must add at least one group in the <em>assignment groups</em> box.';
            Ext.MessageBox.alert('No assignmen groups created', msg);
            this.up('window').close();
        } else {
            this.selectDeadline(parsedArray);
        }
    },

    selectDeadline: function(parsedArray) {
        var me = this;
        var createDeadlineWindow = Ext.widget('multicreatenewdeadlinewindow', {
            width: this.up('window').getWidth(),
            height: this.up('window').getHeight(),
            deadlinemodel: this.deadlinemodel,
            suggestedDeadline: this.suggestedDeadline,
            deadlineRecord: this.deadlineRecord,
            onSaveSuccess: function(record) {
                this.close();
                me.deadlineRecord = record;
                var publishing_time = me.assignmentrecord.data.publishing_time;
                var period_end_time = me.assignmentrecord.data.parentnode__end_time;
                if(record.data.deadline <= publishing_time || record.data.deadline >= period_end_time) {
                    var error = Ext.create('Ext.XTemplate',
                        'Deadline must be between {publishing_time:date} and {period_end_time:date}.'
                    ).apply({publishing_time: publishing_time, period_end_time: period_end_time});
                    Ext.MessageBox.show({
                        title: 'Error',
                        msg: error,
                        buttons: Ext.Msg.OK,
                        icon: Ext.Msg.ERROR
                    });
                } else {
                    me.createAll(parsedArray);
                }
            }
        });
        createDeadlineWindow.show();
    },


    statics: {
        parseUsernamesAndTags: function(rawstr) {
            var tags = [];
            var tagSplit = rawstr.split(/\s*\(\s*/);
            if(tagSplit.length > 1) {
                rawstr = tagSplit[0];
                var tagsString = tagSplit[1];
                tagsString = tagsString.replace(/\)/, "");
                tags = tagsString.split(/\s*,\s*/);
            }
            return {
                usernames: rawstr.split(/\s*,\s*/),
                tags: tags
            };
        }
    },
});
