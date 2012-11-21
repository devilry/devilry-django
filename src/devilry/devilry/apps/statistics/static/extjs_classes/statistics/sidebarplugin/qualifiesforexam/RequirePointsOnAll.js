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
                minValue: 0,
                value: this.settings? this.settings.minimumScaledPoints: '',
                margin: '0 0 10 0'
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
