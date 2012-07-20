Ext.define('devilry_subjectadmin.store.AbstractRelatedUsers', {
    extend: 'Ext.data.Store',

    loadInPeriod: function(periodId, loadConfig) {
        this.setPeriod(periodId);
        this.load(loadConfig);
    },

    setPeriod: function(periodId) {
        this.proxy.url = Ext.String.format(this.proxy.urlpatt, periodId);
    }
});
