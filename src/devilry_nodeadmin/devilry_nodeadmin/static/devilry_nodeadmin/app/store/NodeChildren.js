Ext.define( 'devilry_nodeadmin.store.NodeChildren', {
    extend: 'Ext.data.Store',
    storeId: 'NodeChildren',
    model: 'devilry_nodeadmin.model.Node',
    proxy: {
        type: 'ajax',
        reader: {
            type: 'json'
        }
    },
    autoLoad: true
});