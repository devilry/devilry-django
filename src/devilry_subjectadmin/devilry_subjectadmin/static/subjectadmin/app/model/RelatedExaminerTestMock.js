Ext.define('subjectadmin.model.RelatedExaminerTestMock', {
    extend: 'subjectadmin.model.RelatedExaminer',
    requires: [
        'jsapp.HiddenElementProxy'
    ],
    proxy: {
        type: 'hiddenelement',
        id: 'relatedexaminerproxy'
    }
});
