Ext.define('devilry_subjectadmin.store.ActivePeriodsTestMock', {
    extend: 'Ext.data.Store',
    model: 'devilry_subjectadmin.model.PeriodTestMock',

    proxy: {
        type: 'hiddenelement',
        id: 'activeperiodproxy'
    },

    loadActivePeriods: function(config) {
        return this.load(config);
    }
});
