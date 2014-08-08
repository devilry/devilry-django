Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.RequirePassingGradeOnSubset', {
    extend: 'devilry.statistics.sidebarplugin.qualifiesforexam.FilterBase',
    requires: [
        'devilry.statistics.ChooseAssignmentsGrid'
    ],
    autoScroll: true,

    initComponent: function() {
        Ext.apply(this, {
            items: [{
                xtype: 'statistics-chooseassignmentsgrid',
                margin: '0 0 10 0',
                store: this.loader.assignment_store,
                selectedAssignmentIds: this.settings? this.settings.assignment_ids: undefined
            }, this.defaultButtonPanel]
        });
        this.callParent(arguments);
    },

    _getGrid: function() {
        return this.down('statistics-chooseassignmentsgrid');
    },

    filter: function(student) {
        var assignment_ids = this._getGrid().getIdOfSelected();
        return student.passesAssignments(assignment_ids);
    },

    validInput: function() {
        return this._getGrid().checkAtLeastOneSelected();
    },

    getSettings: function() {
        var assignment_ids = this._getGrid().getIdOfSelected();
        return {
            assignment_ids: assignment_ids
        };
    }
});
