Ext.define('devilry.statistics.AggregatedPeriodDataStore', {
    extend: 'Ext.data.Store',
    model: 'devilry.statistics.AggregatedPeriodDataModel',

    setPeriod: function(period_id) {
        this.proxy.url = Ext.String.format(this.proxy.urlpatt, period_id);
    },

    setLoadEverything: function(loadEverything) {
        this.proxy.extraParams.load_everything = loadEverything? '1': '0';
    },

    loadForPeriod: function(period_id, loadEverything, loadConfig) {
        this.setPeriod(period_id);
        this.setLoadEverything(loadEverything);
        this.load(loadConfig);
    }
});
