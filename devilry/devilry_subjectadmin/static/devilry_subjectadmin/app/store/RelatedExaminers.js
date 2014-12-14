Ext.define('devilry_subjectadmin.store.RelatedExaminers', {
    extend: 'devilry_subjectadmin.store.AbstractRelatedUsers',
    model: 'devilry_subjectadmin.model.RelatedExaminer',

    setPeriod: function(periodId) {
        this.proxy.url = Ext.String.format(this.proxy.urlpatt, periodId);
    }
});
