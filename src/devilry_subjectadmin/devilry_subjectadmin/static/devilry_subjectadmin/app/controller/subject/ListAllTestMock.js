Ext.define('devilry_subjectadmin.controller.subject.ListAllTestMock', {
    extend: 'devilry_subjectadmin.controller.subject.ListAll',

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
