Ext.define( 'devilry_nodeadmin.store.RelatedNodes', {
    extend: 'Ext.data.Store',
    storeId: 'RelatedNodes',
    model: 'devilry_nodeadmin.model.Node',
    proxy: {
        type: 'ajax',
        url: 'rest/nodes/',
        reader: {
            type: 'json'
        }
    },
    autoLoad: true
});
