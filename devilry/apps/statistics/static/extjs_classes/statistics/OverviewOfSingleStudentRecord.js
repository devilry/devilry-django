Ext.define('devilry.statistics.OverviewOfSingleStudentRecord', {
    extend: 'Ext.data.Model',
    idProperty: 'id',
    fields: ['id', 'assignment__long_name', 'assignment__short_name', 'feedback__points']
});
