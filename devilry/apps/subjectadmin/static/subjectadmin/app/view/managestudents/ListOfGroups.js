/**
 * List of groups.
 */
Ext.define('subjectadmin.view.managestudents.ListOfGroups' ,{
    extend: 'Ext.grid.Panel',
    alias: 'widget.listofgroups',
    cls: 'listofgroups',
    store: 'GroupsTestMock',

    columns: [{
        header: 'Groups',  dataIndex: 'id', flex: 1
    }]
});
