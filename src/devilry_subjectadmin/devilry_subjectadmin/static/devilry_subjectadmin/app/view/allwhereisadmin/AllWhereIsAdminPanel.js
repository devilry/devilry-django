Ext.define('devilry_subjectadmin.view.allwhereisadmin.AllWhereIsAdminPanel' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.allwhereisadminpanel', // Define the widget xtype as allwhereisadminpanel
    cls: 'dashboard',

    requires: [
        'devilry_subjectadmin.view.allwhereisadmin.AllWhereIsAdminList'
    ],

    layout: 'fit',
    frame: false,
    border: 0,
    bodyPadding: '20 40 20 40',
    autoScroll: true,

    items: {
        xtype: 'allwhereisadminlist'
    }
});
