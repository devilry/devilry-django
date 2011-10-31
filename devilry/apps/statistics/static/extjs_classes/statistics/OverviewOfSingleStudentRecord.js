Ext.define('devilry.statistics.OverviewOfSingleStudentRecord', {
    extend: 'Ext.data.Model',
    idProperty: 'id',
    fields: ['id', 'assignment__long_name', 'assignmentid', 'assignment__short_name', 'is_open', 'feedback__points', 'feedback']
});
