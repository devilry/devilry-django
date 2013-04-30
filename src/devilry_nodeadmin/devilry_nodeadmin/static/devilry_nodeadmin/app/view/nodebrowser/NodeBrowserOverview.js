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
        cls: 'devilry_nodeadmin_nodebrowsersidebar',
        width: 300,
        layout: 'anchor',
        items: [{
            xtype: 'navigator'
        }, {
            xtype: 'nodechildrenlist'
        }]
    }, {
        xtype: 'nodedetailsoverview',
        columnWidth: 1.0
    }]
});
