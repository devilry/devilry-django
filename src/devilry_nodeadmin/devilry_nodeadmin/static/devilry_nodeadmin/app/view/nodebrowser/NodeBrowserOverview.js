Ext.define('devilry_nodeadmin.view.nodebrowser.NodeBrowserOverview', {
    extend: 'Ext.container.Container',
    alias: 'widget.nodebrowseroverview',
    cls: 'devilry_nodeadmin_nodebrowseroverview',

    requires: [
        'devilry_extjsextras.UnfocusedContainer'
    ],

    layout: 'column',
    autoScroll: true,

    /**
     * @cfg {int} [node_pk]
     */

    margin: '20',

    items: [{
        xtype: 'unfocusedcontainer',
        itemId: 'primary',
        cls: 'devilry_nodeadmin_nodebrowsersidebar',
        width: 300,
        padding: 0
    }, {
        xtype: 'container',
        itemId: 'secondary',
        cls: 'devilry_nodeadmin_secondary',
        columnWidth: 1.0
    }]
});
