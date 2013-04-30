Ext.define( 'devilry_nodeadmin.store.RelatedNodes', {
    extend: 'Ext.data.Store',
    storeId: 'RelatedNodes',
    model: 'devilry_nodeadmin.model.Node',
    proxy: {
        type: 'ajax',
        url: null,
        urlPattern: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_nodeadmin/rest/nodes/?format=json',
        reader: {
            type: 'json'
        }
    },

    collectAll: function( config ) {
        this.proxy.url = this.proxy.urlPattern;
        this.load(config);
    }

});
