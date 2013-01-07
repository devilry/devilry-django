Ext.define( 'devilry_nodeadmin.model.Details', {
    extend: 'Ext.data.Model',
    fields: [
        { name: 'id', type: 'int' },
        { name: 'short_name', type: 'string' },
        { name: 'long_name', type: 'string' },
        { name: 'most_recent_start_time', type: 'date' },
        { name: 'subject_count', type: 'int' },
        { name: 'assignment_count', type: 'int' },
        { name: 'etag', type: 'string' },
        { name: 'subjects' }
    ],
    belongsTo: 'devilry_nodeadmin.model.Node',
    hasMany: 'devilry_nodeadmin.model.Subject'
});
