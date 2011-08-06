Ext.define('devilry.extjshelpers.studentsmanager.ManuallyCreateUsers', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.manuallycreateusers',
    frame: false,
    border: false,

    layout: {
        type: 'vbox',
        align: 'stretch' // Child items are stretched to full width
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

    parseTextToGroupSpec: function(rawValue) {
        var asArray = rawValue.split('\n');
        var resultArray = [];
        Ext.Array.each(asArray, function(groupSpec) {
            groupSpec = Ext.String.trim(groupSpec);
            var studentsAsArray = groupSpec.split(/\s*,\s*/);
            resultArray.push({
                students: studentsAsArray
            });
        });
        return resultArray;
    },

    onCreate: function() {
        var parsedArray = this.parseTextToGroupSpec(this.userinput.getValue());
        console.log(parsedArray);
        var assignmentGroupModelCls = 'devilry.apps.administrator.simplified.SimplifiedAssignmentGroup';
        Ext.Array.each(parsedArray, function(groupSpecArray) {
            if(groupSpecArray.length > 0) {
                //var group = Ext.create(assignmentGroupModelCls, {
                    //students: ?????
                //});
                console.log("TODO: create users");
            }
        });
    }
});
