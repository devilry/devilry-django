Ext.define('devilry_nodeadmin.view.nodeTree', {
    extend: 'Ext.tree.View',
    alias: 'widget.nodetree',
    cls: '',

    itemSelector: 'div',

    initComponent: function() {
        this.store = Ext.create( 'devilry_nodeadmin.store.Tree' );
        this.store.proxy.url = Ext.String.format('/devilry_nodeadmin/rest/tree/' );
        this.callParent(arguments);
    }

});