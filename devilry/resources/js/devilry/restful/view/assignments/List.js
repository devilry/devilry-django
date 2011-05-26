Ext.define('devilry.restful.view.assignments.List' ,{
    extend: 'Ext.grid.Panel',
    title : 'Assignments',
    columns: [
        {header: 'Period',  dataIndex: 'parentnode__short_name',  flex: 1},
        {header: 'Subject',  dataIndex: 'parentnode__parentnode__short_name',  flex: 1},
        {header: 'Name',  dataIndex: 'short_name',  flex: 1},
        {header: 'Id', dataIndex: 'id', flex: 1},
    ]
});
