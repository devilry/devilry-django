Ext.define('devilry.administrator.assignment.PrettyView', {
    extend: 'devilry.administrator.PrettyView',
    alias: 'widget.administrator_assignmentprettyview',


    initComponent: function() {
        Ext.apply(this, {
            relatedButtons: [{
                xtype: 'button',
                text: 'Students',
                listeners: {
                    scope: this,
                    click: this.onStudents
                }
            }]
        });
        this.callParent(arguments);
    },

    onStudents: function() {
        console.log('students');
    }
});
