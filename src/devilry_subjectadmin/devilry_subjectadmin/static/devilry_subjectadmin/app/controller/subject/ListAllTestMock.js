Ext.define('subjectadmin.controller.subject.ListAllTestMock', {
    extend: 'subjectadmin.controller.subject.ListAll',

    views: [
        'subject.ListAllTestMock'
    ],

    stores: [
        'SubjectsTestMock'
    ],

    getSubjectsStore: function() {
        return this.getSubjectsTestMockStore();
    }
});
