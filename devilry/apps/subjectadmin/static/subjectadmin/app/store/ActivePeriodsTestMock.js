Ext.define('subjectadmin.store.ActivePeriodsTestMock', {
    extend: 'Ext.data.Store',
    model: 'subjectadmin.model.PeriodTestMock',

    proxy: {
        type: 'hiddenelement',
        id: 'activeperiodproxy'
    },

    loadActivePeriods: function(config) {
        return this.load(config);
    }
});
