Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.RequirePassingGradeOnAll', {
    extend: 'devilry.statistics.sidebarplugin.qualifiesforexam.FilterBase',
    layout: 'fit',

    initComponent: function() {
        Ext.apply(this, {
            items: this.defaultButtonPanel
        });
        this.callParent(arguments);
    },

    filter: function(student) {
        return student.passesAssignments(this.loader.assignment_ids);
    }
});
