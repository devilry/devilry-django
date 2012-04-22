Ext.define('devilry_subjectadmin.model.RelatedStudentTestMock', {
    extend: 'devilry_subjectadmin.model.RelatedStudent',
    requires: [
        'jsapp.HiddenElementProxy'
    ],
    proxy: {
        type: 'hiddenelement',
        id: 'relatedstudentproxy'
    }
});
