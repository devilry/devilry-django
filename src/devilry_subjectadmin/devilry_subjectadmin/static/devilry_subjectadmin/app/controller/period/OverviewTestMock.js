Ext.define('devilry_subjectadmin.controller.period.OverviewTestMock', {
    extend: 'devilry_subjectadmin.controller.period.Overview',

    views: [
        'period.Overview',
        'period.ListOfAssignmentsTestMock'
    ],

    stores: [
        'AssignmentsTestMock',
        'PeriodsTestMock'
    ],

    getPeriodsStore: function() {
        return this.getPeriodsTestMockStore();
    },

    getAssignmentsStore: function() {
        return this.getAssignmentsTestMockStore();
    }
});
