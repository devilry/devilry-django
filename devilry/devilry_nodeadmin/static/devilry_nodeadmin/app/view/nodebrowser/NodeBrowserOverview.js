Ext.define('devilry_nodeadmin.view.nodebrowser.NodeBrowserOverview', {
    extend: 'Ext.container.Container',
    alias: 'widget.nodebrowseroverview',
    cls: 'devilry_nodeadmin_nodebrowseroverview',

    autoScroll: true,
    margin: '0',
    padding: '20',

    /**
     * @cfg {int} [node_pk]
     */

    items: [{
        xtype: 'nodedetailsoverview',
        columnWidth: 1.0
    }]
});
