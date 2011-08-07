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

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },

    initComponent: function() {
        this.userinput = Ext.widget('textareafield', {
            style: 'margin:0', // Remove default margin
            hideLabel: true,
            flex: 1 // Take up all remaining vertical space
        });
        this.userinput.setValue('dewey\nlouie \n\n huey \ndonald, della');
        Ext.apply(this, {
            items: this.userinput,
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
