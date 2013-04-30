Ext.define( 'devilry_nodeadmin.store.ToplevelNodes', {
    extend: 'Ext.data.Store',
    model: 'devilry_nodeadmin.model.ToplevelNode',
    proxy: {
        type: 'rest',
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_nodeadmin/rest/toplevel_nodes/',
        extraParams: {
            format: 'json'
        },
        reader: {
            type: 'json'
        }
    }
});
