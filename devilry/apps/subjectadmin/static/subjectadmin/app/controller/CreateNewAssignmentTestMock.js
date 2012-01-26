Ext.define('subjectadmin.controller.CreateNewAssignmentTestMock', {
    extend: 'subjectadmin.controller.CreateNewAssignment',

    views: [
        'createnewassignment.Form',
        'createnewassignment.ActivePeriodsListTestMock'
    ],

    stores: [
        'ActivePeriodsTestMock'
    ],

    getActivePeriodsStore: function() {
        return this.getActivePeriodsTestMockStore();
    }
});
