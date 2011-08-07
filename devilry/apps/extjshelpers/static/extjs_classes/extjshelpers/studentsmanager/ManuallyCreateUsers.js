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
            flex: 1 // Take up all remaining vertical space
        });
        //this.userinput.setValue('dewey\nlouie \n\n huey \ndonald, della');
        Ext.apply(this, {
            //items: this.userinput,

            layout: {
                type: 'hbox',
                align: 'stretch'
            },

            defaults: {
                padding: 20,
            },

            items: [{
                flex: 10,
                xtype: 'box',
                padding: 20,
                autoScroll: true,
                html: this.helptext
            }, {
                xtype: 'panel',
                frame: false,
                border: false,
                flex: 10,
                layout: {
                    type: 'vbox',
                    align: 'stretch'
                },
                items: [{
                    xtype: 'box',
                    html: '<section><h1>Assignment groups</h1></section>'
                }, this.userinput]
            }],

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

    parseGroupSpec: function(groupSpec) {
        groupSpec = Ext.String.trim(groupSpec);
        if(groupSpec == "") {
            return null;
        }
        var asArray = groupSpec.split(/\s*,\s*/);
        groupSpecObj = {
            name: null,
            is_open: true,
            fake_candidates: [],
            fake_examiners: []
        };
        Ext.Array.each(asArray, function(candidateSpec) {
            var username = candidateSpec;
            groupSpecObj.fake_candidates.push({
                username: username,
                candidate_id: null
            });
        });
        return groupSpecObj;
    },

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

    createAll: function(parsedArray) {
        var assignmentGroupModelCls = 'devilry.apps.administrator.simplified.SimplifiedAssignmentGroup';
        Ext.Array.each(parsedArray, function(groupSpecObj) {
            var completeGroupSpecObj = {
                parentnode: this.assignmentid
            };
            Ext.apply(completeGroupSpecObj, groupSpecObj);
            //console.log(completeGroupSpecObj);
            var group = Ext.create(assignmentGroupModelCls, completeGroupSpecObj);
            group.save();
        }, this);
    },

    onCreate: function() {
        var parsedArray = this.parseTextToGroupSpec(this.userinput.getValue());
        console.log(parsedArray);
        this.createAll(parsedArray);
    }
});
