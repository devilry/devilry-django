Ext.define( 'devilry_nodeadmin.store.PathStore', {
    extend: 'Ext.data.Store',
    storeId: 'PathStore',
    model: 'devilry_nodeadmin.model.Path',
    proxy: {
        url: '/rest/',
        type: 'rest',
        reader: {
            type: 'json',
            root: '.'
        }
    },
    autoLoad: true
});