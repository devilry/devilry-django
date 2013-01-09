Ext.define('devilry_nodeadmin.view.dashboard.DashboardOverview', {
    extend: 'Ext.container.Container',
    alias: 'widget.dashboardoverview',
    cls: 'devilry_nodeadmin_nodebrowseroverview',

    requires: [
        'devilry_nodeadmin.view.dashboard.DefaultNodeList'
    ],

    layout: 'column',
    autoScroll: true,

    items: [{
        xtype: 'container',
        cls: 'devilry_nodeadmin_primary',
        itemId: 'primary',
        columnWidth: 0.5,
        padding: '30 20 20 30',
        items: [{
            xtype: 'defaultnodelist'
        }]
    }, {
        xtype: 'box',
        itemId: 'secondary',
        cls: 'devilry_nodeadmin_secondary',
        cls: 'bootstrap',
        columnWidth: 0.5,
        padding: '30 20 20 30'
    }]
});