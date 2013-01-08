Ext.define( 'devilry_nodeadmin.model.Node', {
    extend: 'Ext.data.Model',
    fields: [
        { name: 'id', type: 'int' },
        { name: 'short_name', type: 'string' },
        { name: 'long_name', type: 'string' },
        { name: 'most_recent_start_time', type: 'date' },
        { name: 'etag', type: 'string' },
        { name: 'predecessor' },
        { name: 'children'}
    ],
    hasOne: 'devilry_nodeadmin.model.Node',
    hasMany: 'devilry_nodeadmin.model.Node'
});
