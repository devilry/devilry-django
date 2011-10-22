Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.RequirePassingGradeOnSubset', {
    extend: 'devilry.statistics.sidebarplugin.qualifiesforexam.FilterBase',
    layout: 'fit',
    requires: [
        'devilry.statistics.ChooseAssignmentsGrid'
    ],

    initComponent: function() {
        Ext.apply(this, {
            items: [{
                xtype: 'statistics-chooseassignmentsgrid',
                margin: {bottom: 10},
                store: this.loader.assignment_store
            }, this.defaultButtonPanel]
        });
        this.callParent(arguments);
    },

    filter: function(student) {
        var assignment_ids = this.down('statistics-chooseassignmentsgrid').getIdOfSelected();
        return student.passesAssignments(assignment_ids);
    }
});
