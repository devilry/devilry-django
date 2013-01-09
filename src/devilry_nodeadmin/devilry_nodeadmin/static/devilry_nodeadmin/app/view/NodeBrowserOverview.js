Ext.define('devilry_nodeadmin.view.NodeBrowserOverview', {
    extend: 'Ext.container.Container',
    alias: 'widget.nodebrowseroverview',
    cls: 'devilry_nodeadmin_nodebrowseroverview',

    items: [{
        xtype: 'container',
        cls: 'bootstrap',
        itemId: 'primary',
        region: 'east',
        columnWidth: 0.5,
        padding: '30 20 20 30'
    }, {
        xtype: 'container',
        itemId: 'secondary',
        cls: 'bootstrap',
        region: 'west',
        columnWidth: 0.5,
        padding: '30 20 20 30'
    }]
});