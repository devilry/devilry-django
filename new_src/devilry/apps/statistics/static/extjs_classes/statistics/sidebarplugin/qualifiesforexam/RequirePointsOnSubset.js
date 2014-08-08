Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.RequirePointsOnSubset', {
    extend: 'devilry.statistics.sidebarplugin.qualifiesforexam.RequirePointsBase',
    requires: [
        'devilry.statistics.ChooseAssignmentsGrid'
    ],
    autoScroll: true,

    initComponent: function() {
        Ext.apply(this, {
            items: [{
                xtype: 'statistics-chooseassignmentsgrid',
                margin: '0 0 10 0',
                selectedAssignmentIds: this.settings? this.settings.assignment_ids: undefined,
                store: this.loader.assignment_store
            }, {
                xtype: 'numberfield',
                fieldLabel: 'Minumum total points on selected',
                minValue: 0,
                value: this.settings? this.settings.minimumScaledPoints: '',
                margin: '0 0 10 0'
            }, this.defaultButtonPanel]
        });
        this.callParent(arguments);
    },

    _getGrid: function() {
        return this.down('statistics-chooseassignmentsgrid');
    },


    filter: function(student) {
        var assignment_ids = this.down('statistics-chooseassignmentsgrid').getIdOfSelected();
        var minimumScaledPoints = this.down('numberfield').getValue();
        return student.hasMinimalNumberOfScaledPointsOn(assignment_ids, minimumScaledPoints);
    },

    validInput: function() {
        return this.validPointInput() && this.down('statistics-chooseassignmentsgrid').checkAtLeastOneSelected();
    },

    getSettings: function() {
        var settings = this.callParent(arguments);
        settings.assignment_ids = this._getGrid().getIdOfSelected();
        return settings;
    }
});
