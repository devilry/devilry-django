Ext.define('devilry.extjshelpers.assignmentgroup.CreateNewDeadlineWindow', {
    extend: 'devilry.extjshelpers.RestfulSimplifiedEditWindowBase',
    alias: 'widget.createnewdeadlinewindow',
    cls: 'widget-createnewdeadlinewindow',
    title: 'Create deadline',
    width: 700,
    height: 450,

    requires: [
        'devilry.extjshelpers.RestfulSimplifiedEditPanel',
        'devilry.extjshelpers.forms.Deadline'
    ],

    assignmentgroupid: undefined,
    deadlinemodel: undefined,

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },
    
    initComponent: function() {
        var deadlineRecord = Ext.create(this.deadlinemodel, {
            'assignment_group': this.assignmentgroupid
        });

        Ext.apply(this, {
            editpanel: Ext.widget('restfulsimplified_editpanel', {
                model: this.deadlinemodel,
                editform: Ext.create('devilry.extjshelpers.forms.Deadline'),
                record: deadlineRecord
            })
        });
        this.callParent(arguments);
    }
});
