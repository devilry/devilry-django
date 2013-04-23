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
        itemId: 'primary',
        cls: 'devilry_nodeadmin_primary',
        columnWidth: 0.65,
        padding: '30 20 20 30'
    }, {
        xtype: 'container',
        itemId: 'secondary',
        cls: 'devilry_nodeadmin_secondary',
        columnWidth: 0.35,
        padding: '30 20 20 30'
    }]
});
