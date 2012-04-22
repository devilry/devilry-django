Ext.define('devilry_subjectadmin.model.RelatedExaminerTestMock', {
    extend: 'devilry_subjectadmin.model.RelatedExaminer',
    requires: [
        'jsapp.HiddenElementProxy'
    ],
    proxy: {
        type: 'hiddenelement',
        id: 'relatedexaminerproxy'
    }
});
