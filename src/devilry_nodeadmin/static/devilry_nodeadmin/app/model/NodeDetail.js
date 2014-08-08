Ext.define( 'devilry_nodeadmin.model.NodeDetail', {
    extend: 'Ext.data.Model',
    fields: [
        { name: 'id', type: 'int' },
        { name: 'short_name', type: 'string' },
        { name: 'long_name', type: 'string' },
        { name: 'assignment_count', type: 'int' },
        { name: 'subject_count', type: 'int' },
        { name: 'etag', type: 'string' },
        { name: 'subjects', type: 'auto'},
        { name: 'childnodes', type: 'auto'},
        { name: 'path', type: 'auto'}
    ],
    proxy: {
        type: 'rest',
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_nodeadmin/rest/node/details/',
        extraParams: {
            format: 'json'
        },
        reader: {
            type: 'json'
        }
    }
});
