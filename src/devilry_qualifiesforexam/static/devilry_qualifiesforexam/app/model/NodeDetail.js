Ext.define('devilry_qualifiesforexam.model.NodeDetail', {
    extend: 'Ext.data.Model',
    fields: [
        { name: 'id', type: 'int' },
        { name: 'short_name', type: 'string' },
        { name: 'path', type: 'auto'}
    ],
    proxy: {
        type: 'rest',
        url: window.DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_nodeadmin/rest/node/details/',
        extraParams: {
            format: 'json'
        },
        reader: {
            type: 'json'
        }
    }
});
