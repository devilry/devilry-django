Ext.define('subjectadmin.controller.ShortcutsTestMock', {
    extend: 'subjectadmin.controller.Shortcuts',

    stores: [
        'ActiveAssignmentsTestMock'
    ],

    getActiveAssignmentsStore: function() {
        return this.getActiveAssignmentsTestMockStore();
    }
});
