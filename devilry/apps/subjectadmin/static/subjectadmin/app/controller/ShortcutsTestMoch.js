Ext.define('subjectadmin.controller.ShortcutsTestMoch', {
    extend: 'subjectadmin.controller.Shortcuts',

    stores: [
        'ActiveAssignmentsTestMoch'
    ],

    getActiveAssignmentsStore: function() {
        return this.getActiveAssignmentsTestMochStore();
    }
});
