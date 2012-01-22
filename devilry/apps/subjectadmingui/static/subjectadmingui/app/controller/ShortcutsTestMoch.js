Ext.define('subjectadmingui.controller.ShortcutsTestMoch', {
    extend: 'subjectadmingui.controller.Shortcuts',

    stores: [
        'ActiveAssignmentsTestMoch'
    ],

    getActiveAssignmentsStore: function() {
        return this.getActiveAssignmentsTestMochStore();
    }
});
