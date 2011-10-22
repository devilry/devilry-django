Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.RequirePointsOnSubset', {
    extend: 'devilry.statistics.sidebarplugin.qualifiesforexam.RequirePointsBase',
    requires: [
        'devilry.statistics.ChooseAssignmentsGrid'
    ],

    initComponent: function() {
        Ext.apply(this, {
            items: [{
                xtype: 'statistics-chooseassignmentsgrid',
                margin: {bottom: 10},
                store: this.loader.assignment_store
            }, {
                xtype: 'numberfield',
                fieldLabel: 'Minumum total points on selected',
                minValue: 0,
                margin: {bottom: 10}
            }, this.defaultButtonPanel]
        });
        this.callParent(arguments);
    },

    filter: function(student) {
        var assignment_ids = this.down('statistics-chooseassignmentsgrid').getIdOfSelected();
        var minimumScaledPoints = this.down('numberfield').getValue();
        return student.hasMinimalNumberOfScaledPointsOn(assignment_ids, minimumScaledPoints);
    },

    validInput: function() {
        return this.validPointInput() && this.down('statistics-chooseassignmentsgrid').checkAtLeastOneSelected();
    }
});
