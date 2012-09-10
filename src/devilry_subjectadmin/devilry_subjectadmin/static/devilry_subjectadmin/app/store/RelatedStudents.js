Ext.define('devilry_subjectadmin.store.RelatedStudents', {
    extend: 'devilry_subjectadmin.store.AbstractRelatedUsers',
    model: 'devilry_subjectadmin.model.RelatedStudent',

    setPeriod: function(periodId) {
        this.proxy.url = Ext.String.format(this.proxy.urlpatt, periodId);
    }
});
