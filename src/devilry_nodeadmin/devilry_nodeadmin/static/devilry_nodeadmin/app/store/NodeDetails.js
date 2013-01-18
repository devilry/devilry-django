Ext.define( 'devilry_nodeadmin.store.NodeDetails', {
    extend: 'Ext.data.Store',
    storeId: 'NodeDetails',
    model: 'devilry_nodeadmin.model.Details',
    proxy: {
        type: 'ajax',
        url: null,
        urlPattern: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_nodeadmin/rest/node/{0}/details?format=json',
        reader: {
            type: 'json'
        }
    },

    collectByNode: function( node_pk, config ) {
        this.proxy.url = Ext.String.format( this.proxy.urlPattern, node_pk );
        this.load(config);
    }
});