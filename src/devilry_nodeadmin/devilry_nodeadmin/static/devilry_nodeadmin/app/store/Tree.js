Ext.define( 'devilry_nodeadmin.store.Tree', {
    extend: 'Ext.data.TreeStore',
    storeId: 'Tree',
    model: 'devilry_nodeadmin.model.Tree',
    proxy: {
        url: null,
        type: 'rest',
        reader: {
            type: 'json',
            root: '.'
        }
    },
    autoLoad: true
});