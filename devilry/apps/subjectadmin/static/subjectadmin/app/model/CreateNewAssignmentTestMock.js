Ext.define('subjectadmin.model.CreateNewAssignmentTestMock', {
    extend: 'subjectadmin.model.CreateNewAssignment',
    requires: [
        'jsapp.HiddenElementProxy'
    ],
    proxy: {
        type: 'hiddenelement',
        id: 'createnewassginmentproxy'
    }
});
