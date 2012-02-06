Ext.define('subjectadmin.model.RelatedExaminerTestMock', {
    extend: 'subjectadmin.model.RelatedExaminer',
    requires: [
        'jsapp.HiddenElementProxy'
    ],
    proxy: {
        type: 'hiddenelement',
        show: true,
        id: 'relatedexaminerproxy'
    }
});
