Ext.define( 'devilry_nodeadmin.store.NodeChildren', {
    extend: 'Ext.data.Store',
    storeId: 'NodeChildren',
    model: 'devilry_nodeadmin.model.Node',
    proxy: {
        type: 'ajax',
        url: 'rest/nodes/',
        reader: {
            type: 'json',
            root: 'children'
        }
    },
    autoLoad: true
});