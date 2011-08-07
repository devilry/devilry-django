Ext.define('devilry.extjshelpers.studentsmanager.ManuallyCreateUsers', {
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
         * 
         */
        assignmentid: undefined
    },

    helptext:
        '<section class="helpsection">' +
        '   <h1>Help</h1>' +
        '   <p>Students are organized in <em>assignment groups</em>. You should specify <strong>one</strong> <em>assignment group</em> on each line in the input box on the right hand side.</p>' +
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
        '   </ul>' +
        '</section>',

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },

    initComponent: function() {
        this.userinput = Ext.widget('textareafield', {
            hideLabel: true,
            emptyText: 'My optional group name:: somestudent, anotherstudent',
            flex: 10 // Take up all remaining vertical space
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
                flex: 10,
                xtype: 'box',
                padding: 20,
                autoScroll: true,
                html: this.helptext
            }, this.userinput],

            dockedItems: [{
                xtype: 'toolbar',
                dock: 'bottom',
                ui: 'footer',
                items: ['->', {
                    xtype: 'button',
                    scale: 'large',
                    text: 'Create assignment groups',
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
    parseCandidateSpec: function(candidateSpec) {
        var asArray = candidateSpec.split(/\s*:\s*/);
        var candidate_id = asArray.length > 1? asArray[1]: null;
        return {
            username: asArray[0],
            candidate_id: candidate_id
        };
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
            fake_examiners: []
        };

        var nameSplit = groupSpec.split(/\s*::\s*/);
        if(nameSplit.length > 1) {
            groupSpecObj.name = nameSplit[0];
            groupSpec = nameSplit[1];
        }
        var asArray = groupSpec.split(/\s*,\s*/);
        Ext.Array.each(asArray, function(candidateSpec) {
            groupSpecObj.fake_candidates.push(this.parseCandidateSpec(candidateSpec));
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
        var assignmentGroupModelCls = 'devilry.apps.administrator.simplified.SimplifiedAssignmentGroup';
        var finishedCounter = 0;
        var unsuccessful = [];
        Ext.Array.each(parsedArray, function(groupSpecObj) {
            var completeGroupSpecObj = {
                parentnode: this.assignmentid
            };
            Ext.apply(completeGroupSpecObj, groupSpecObj);
            var group = Ext.create(assignmentGroupModelCls, completeGroupSpecObj);
            group.save({
                scope: this,
                success: function() {
                    finishedCounter ++;
                    if(finishedCounter == parsedArray.length) {
                        this.onFinishedSavingAll(unsuccessful, finishedCounter);
                    }
                },
                failure: function() {
                    finishedCounter ++;
                    unsuccessful.push(groupSpecObj);
                    if(finishedCounter == parsedArray.length) {
                        this.onFinishedSavingAll(unsuccessful, finishedCounter);
                    }
                }
            });
        }, this);
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
    onFinishedSavingAll: function(unsuccessful, totalCount) {
        if(unsuccessful.length == 0) {
            this.onSuccess(totalCount);
        } else {
            this.onFailure(unsuccessful, totalCount);
        }
    },

    /**
     * @private
     */
    onSuccess: function(totalCount) {
        var me = this;
        Ext.MessageBox.show({
            title: 'Success',
            msg: Ext.String.format('Created {0} assignment groups.', totalCount),
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
    onFailure: function(unsuccessful, totalCount) {
        //console.log(totalCount);
        //console.log(unsuccessful);
        this.userinput.setValue(this.groupSpecObjArrayToString(unsuccessful));
        Ext.MessageBox.show({
            title: 'Error',
            msg: Ext.String.format(
                'Failed to create {0} of {1} assignment groups. This is usually caused by invalid usernames. The groups with errors have been re-added to the input box.',
                unsuccessful.length, totalCount),
            buttons: Ext.Msg.OK,
            icon: Ext.Msg.ERROR
        });
    },

    /**
     * @private
     */
    onCreate: function() {
        var parsedArray = this.parseTextToGroupSpec(this.userinput.getValue());
        //console.log(parsedArray);
        this.createAll(parsedArray);
    }
});
