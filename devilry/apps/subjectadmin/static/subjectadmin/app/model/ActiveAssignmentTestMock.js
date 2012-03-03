Ext.define('subjectadmin.model.ActiveAssignmentTestMock', {
    extend: 'subjectadmin.model.ActiveAssignment',
    requires: [
        'jsapp.HiddenElementProxy'
    ],
    proxy: {
        type: 'hiddenelement',
        id: 'shortcutassignmentproxy'
    }
});
