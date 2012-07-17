Ext.define('devilry_subjectadmin.store.RelatedStudents', {
    extend: 'Ext.data.Store',
    model: 'devilry_subjectadmin.model.RelatedStudent',

    loadInPeriod: function(periodId, loadConfig) {
        this.proxy.url = Ext.String.format(this.proxy.urlpatt, periodId);
        this.load(loadConfig);
    }
});
