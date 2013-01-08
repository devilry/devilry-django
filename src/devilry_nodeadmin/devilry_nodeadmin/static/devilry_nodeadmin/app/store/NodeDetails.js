Ext.define( 'devilry_nodeadmin.store.NodeDetails', {
    extend: 'Ext.data.Store',
    storeId: 'NodeDetails',
    model: 'devilry_nodeadmin.model.Details',
    proxy: {
        type: 'rest',
        url: '/rest/node/{node_pk}/details',
        reader: {
            type: 'json'
        }
    },
    autoLoad: true
});