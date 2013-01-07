Ext.define( 'devilry_nodeadmin.model.Parent', {
    extend: 'Ext.data.Model',
    fields: [
        { name: 'id', type: 'int' },
        { name: 'short_name', type: 'string' },
        { name: 'long_name', type: 'string' },
        { name: 'most_recent_start_time', type: 'date' },
        { name: 'etag', type: 'string' }
    ],
    belongsTo: 'devilry_nodeadmin.model.Node'
});
