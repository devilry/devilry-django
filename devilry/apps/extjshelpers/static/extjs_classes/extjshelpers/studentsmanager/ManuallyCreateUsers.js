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
        '   <p>Students are organized in <em>assignment groups</em>.</p>' +
        '   <p>Very often, an assignment requires <strong>individual</strong> deliveries and feedback. In this case, each <em>assignment group</em> should contain a single student.</p>' +
        '   <p>When students are supposed to <strong>cooperate</strong> on the same assignment, they should be in the same <em>assignment group</em>.</p>' +
        '   <p>It is often useful to give an <em>assignment group</em> a <strong>name</strong>. The name is primarily intended for project assignments, where it is useful to name a group after their project. However, the name can be used for other purposes, such as <em>tagging</em> of groups of special interest. Since you can search for groups by name, you can name multiple groups with tags, such as <em>exceptional</em>, and find these groups using the search field.</p>' +
        '   <h2>Input format</h2>' +
        '   <p>The format used to create the assignment groups is:</p>' +
        '   <ul>' +
        '       <li>One assignment group on each line.</li>' +
        '       <li>Each username is separated by a comma.</li>' +
        '       <li>Group name is identified by two colons at the end of the name, and must be placed at the beginning of the line.</li>' +
        '       <li>A group name or at least one username is required for each group.</li>' +
        '       <li>An optional candidate id for a candidate is denoted by a colon and the candidate id after the username.</li>' +
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
