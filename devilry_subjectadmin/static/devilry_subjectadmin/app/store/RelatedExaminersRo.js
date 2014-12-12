Ext.define('devilry_subjectadmin.store.RelatedExaminersRo', {
    extend: 'devilry_subjectadmin.store.AbstractRelatedUsers',
    model: 'devilry_subjectadmin.model.RelatedExaminerRo',

    setAssignment: function(assignmentId) {
        this.proxy.url = Ext.String.format(this.proxy.urlpatt, assignmentId);
    }
});
