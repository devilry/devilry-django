Ext.define('subjectadmin.model.RelatedStudentTestMock', {
    extend: 'subjectadmin.model.RelatedStudent',
    requires: [
        'jsapp.HiddenElementProxy'
    ],
    proxy: {
        type: 'hiddenelement',
        id: 'relatedstudentproxy'
    }
});
