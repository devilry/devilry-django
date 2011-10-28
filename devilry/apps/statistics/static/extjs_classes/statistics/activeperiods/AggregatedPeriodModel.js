Ext.define('devilry.statistics.activeperiods.AggregatedPeriodModel', {
    extend: 'Ext.data.Model',
    fields: ['period_id', 'subject_long_name', 'period_long_name', 'ready_for_export'],
    idProperty: 'period_id'
});
