Ext.define('subjectadmin.controller.period.OverviewTestMock', {
    extend: 'subjectadmin.controller.period.Overview',

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
