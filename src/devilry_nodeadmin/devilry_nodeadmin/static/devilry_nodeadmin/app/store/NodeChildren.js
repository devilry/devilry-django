Ext.define( 'devilry_nodeadmin.store.NodeChildren', {
    extend: 'Ext.data.Store',
    storeId: 'NodeChildren',
    model: 'devilry_nodeadmin.model.Node',
    proxy: {
        type: 'ajax',
        url: null,
        urlPattern: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_nodeadmin/rest/node/{0}/children?format=json',
        reader: {
            type: 'json',
            root: 'children'
        }
    },

    collectByNode: function(node_pk, config) {
        this.proxy.url = Ext.String.format(this.proxy.urlPattern, node_pk);
        this.load(config);
    }
});