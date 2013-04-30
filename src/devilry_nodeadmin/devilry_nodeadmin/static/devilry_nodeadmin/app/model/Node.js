Ext.define( 'devilry_nodeadmin.model.Node', {
    extend: 'Ext.data.Model',
    fields: [
        { name: 'id', type: 'int' },
        { name: 'short_name', type: 'string' },
        { name: 'long_name', type: 'string' },
        { name: 'most_recent_start_time', type: 'date' },
        { name: 'assignment_count', type: 'int' },
        { name: 'subject_count', type: 'int' },
        { name: 'etag', type: 'string' },
        { name: 'predecessor', type: 'auto'},
        { name: 'children', type: 'auto'},
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
