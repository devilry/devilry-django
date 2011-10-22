Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.RequirePointsOnAll', {
    extend: 'devilry.statistics.sidebarplugin.qualifiesforexam.RequirePointsBase',
    requires: [
        'devilry.statistics.ChooseAssignmentsGrid'
    ],

    initComponent: function() {
        Ext.apply(this, {
            items: [{
                xtype: 'numberfield',
                fieldLabel: 'Minumum total points',
                margin: {bottom: 10}
            }, this.defaultButtonPanel]
        });
        this.callParent(arguments);
    },

    filter: function(student) {
        var assignment_ids = this.loader.assignment_ids;
        var minimumScaledPoints = this.down('numberfield').getValue();
        return student.hasMinimalNumberOfScaledPointsOn(assignment_ids, minimumScaledPoints);
    },

    validInput: function() {
        return this.validPointInput();
    }
});
