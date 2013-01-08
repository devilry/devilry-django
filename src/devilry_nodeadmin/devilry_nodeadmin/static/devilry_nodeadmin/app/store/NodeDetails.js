Ext.define( 'devilry_nodeadmin.store.NodeDetails', {
    extend: 'Ext.data.Store',
    storeId: 'NodeDetails',
    model: 'devilry_nodeadmin.model.Details',
    proxy: {
        type: 'ajax',
        url: 'rest/nodes/',
        reader: {
            type: 'json'
        }
    },
    autoLoad: true
});