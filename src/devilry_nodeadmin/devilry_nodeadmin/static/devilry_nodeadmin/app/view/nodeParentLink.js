Ext.define('devilry_nodeadmin.view.nodeParentLink', {
    extend: 'Ext.view.View',
    alias: 'widget.nodeparentlink',
    cls: 'node-parent-link',
    tpl: [
        '<tpl for=".">',
        '<tpl if="predecessor">',
        '<a href="/devilry_nodeadmin/#/node/{ predecessor.id }"><i class="icon-chevron-up"></i> ett nivå opp</a>',
        '<tpl else>',
        '<a href="/devilry_nodeadmin/#/node/"><i class="icon-chevron-up"></i> ett nivå opp</a>',
        '</tpl>',
        '</tpl>'
    ],

    itemSelector: 'a',

    initComponent: function() {
        this.store = Ext.create( 'devilry_nodeadmin.store.NodeDetails' );
        this.store.proxy.url = Ext.String.format('/devilry_nodeadmin/rest/node/{0}/details', this.node_pk );
        this.callParent(arguments);
    }

});