Ext.define('devilry.restful.view.assignments.Grid' ,{
    extend: 'Ext.grid.Panel',
    title : 'Assignments',
    columns: [
        {header: 'Subject',  dataIndex: 'parentnode__parentnode__short_name',  flex: 1},
        {header: 'Period',  dataIndex: 'parentnode__short_name',  flex: 1},
        {header: 'Name',  dataIndex: 'short_name',  flex: 1},
        //{header: 'Id', dataIndex: 'id', flex: 1},
    ]
});
