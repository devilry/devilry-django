Ext.define('devilry_nodeadmin.view.dashboard.DashboardOverview', {
    extend: 'Ext.container.Container',
    alias: 'widget.dashboardoverview',
    cls: 'devilry_nodeadmin_nodebrowseroverview',

    layout: 'column',
    autoScroll: true,

    items: [{
        xtype: 'toplevelnodelist',
        columnWidth: 0.65,
        padding: '30 20 20 30'
    }, {
        xtype: 'betawarning',
        columnWidth: 0.35,
        padding: '30 20 20 30'
    }]
});
