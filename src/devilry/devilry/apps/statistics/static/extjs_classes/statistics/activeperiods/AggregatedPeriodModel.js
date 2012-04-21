Ext.define('devilry.statistics.activeperiods.AggregatedPeriodModel', {
    extend: 'Ext.data.Model',
    fields: ['period_id', 'subject_long_name', 'period_long_name', 'qualifies_for_exam_ready_for_export'],
    idProperty: 'period_id'
});
