Ext.define('devilry_subjectadmin.store.RelatedStudentsRo', {
    extend: 'devilry_subjectadmin.store.AbstractRelatedUsers',
    model: 'devilry_subjectadmin.model.RelatedStudentRo',

    setAssignment: function(assignmentId) {
        this.proxy.url = Ext.String.format(this.proxy.urlpatt, assignmentId);
    }
});
