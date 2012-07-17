Ext.define('devilry_subjectadmin.store.RelatedExaminers', {
    extend: 'Ext.data.Store',
    model: 'devilry_subjectadmin.model.RelatedExaminer',

    loadInPeriod: function(periodId, loadConfig) {
        this.proxy.url = Ext.String.format(this.proxy.urlpatt, periodId);
        this.load(loadConfig);
    }
});
