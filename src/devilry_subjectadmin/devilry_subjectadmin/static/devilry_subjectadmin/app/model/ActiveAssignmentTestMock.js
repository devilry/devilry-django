Ext.define('devilry_subjectadmin.model.ActiveAssignmentTestMock', {
    extend: 'devilry_subjectadmin.model.ActiveAssignment',
    requires: [
        'jsapp.HiddenElementProxy'
    ],
    proxy: {
        type: 'hiddenelement',
        id: 'shortcutassignmentproxy'
    }
});
