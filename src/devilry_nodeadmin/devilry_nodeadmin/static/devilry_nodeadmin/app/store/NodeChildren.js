Ext.define( 'devilry_nodeadmin.store.NodeChildren', {
    extend: 'Ext.data.Store',
    storeId: 'NodeChildren',
    model: 'devilry_nodeadmin.model.Node',
    proxy: {
        type: 'ajax',
        urlpatt: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_nodeadmin/rest/node/{0}/children',
        reader: {
            type: 'json',
            root: 'children'
        }
    },

    loadWithNode: function(node_pk, config) {
        this.proxy.url = Ext.String.format(this.proxy.urlpatt, node_pk);
        this.load(config);
    }
});