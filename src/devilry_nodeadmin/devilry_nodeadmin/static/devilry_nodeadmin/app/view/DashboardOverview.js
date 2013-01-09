Ext.define('devilry_nodeadmin.view.DashboardOverview', {
    extend: 'Ext.container.Container',
    alias: 'widget.dashboardoverview',
    cls: 'devilry_nodeadmin_nodebrowseroverview',

    requires: [
        'devilry_nodeadmin.view.DefaultNodeList'
    ],

    layout: 'column',
    autoScroll: true,

    items: [{
        xtype: 'container',
        cls: 'bootstrap',
        itemId: 'primary',
        columnWidth: 0.5,
        padding: '30 20 20 30',
        items: [{
            xtype: 'defaultnodelist'
        }]
    }, {
        xtype: 'box',
        itemId: 'secondary',
        cls: 'bootstrap',
        columnWidth: 0.5,
        padding: '30 20 20 30'
    }]
});