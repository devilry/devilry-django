Ext.define('devilry.administrator.studentsmanager.ManuallyCreateUsers', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.manuallycreateusers',
    frame: false,
    border: false,

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

        assignmentrecord: undefined,
        deadlinemodel: undefined,
        suggestedDeadline: undefined
    },

    helptext:
        '<div class="section helpsection">' +
        //'   <h1>Help</h1>' +
        '   <p>Students are organized in <em>assignment groups</em>. You should specify <strong>one</strong> <em>assignment group</em> on each line in the input box.</p>' +
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
            flex: 10, // Take up all remaining vertical space
            margin: 10,
            value: currentValue
        });
        //this.userinput.setValue('dewey\nlouie:401, hue\n\nSaker azz:: donald, dela:30');
        //this.userinput.setValue('dewey\nlouie:401');
        Ext.apply(this, {
            //items: this.userinput,

            layout: {
                type: 'hbox',
                align: 'stretch'
            },

            items: [this.userinput, {
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
        Ext.Array.each(parsedArray, function(groupSpecObj) {
            this.createGroup(groupSpecObj);
        }, this);
    },

    /**
     * @private
     */
    createGroup: function(groupSpecObj) {
        var completeGroupSpecObj = {
            parentnode: this.assignmentrecord.data.id
        };
        Ext.apply(completeGroupSpecObj, groupSpecObj);
        var group = Ext.create(this.assignmentGroupModelCls, completeGroupSpecObj);
        group.save({
            scope: this,
            success: this.createDeadline,
            failure: function() {
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
        });
    },

    /**
     * @private
     */
    createDeadline: function(assignmentGroupRecord) {
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
        this.selectDeadline(parsedArray);
    },

    /**
     * @private
     */
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
