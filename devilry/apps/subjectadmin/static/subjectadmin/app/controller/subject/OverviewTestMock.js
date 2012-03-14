Ext.define('subjectadmin.controller.subject.OverviewTestMock', {
    extend: 'subjectadmin.controller.subject.Overview',

    stores: [
        'SubjectsTestMock'
    ],

    getSubjectsStore: function() {
        return this.getSubjectsTestMockStore();
    }
});
