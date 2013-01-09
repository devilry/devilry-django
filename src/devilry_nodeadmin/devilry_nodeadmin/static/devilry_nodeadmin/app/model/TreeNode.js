Ext.define( 'devilry_nodeadmin.model.TreeNode', {
    extend: 'Ext.data.NodeInterface',
    expanded: true,
    fields: [
        { name: 'id', type: 'int' },
        { name: 'short_name', type: 'string' },
        { name: 'children' }
    ],
    hasMany: 'devilry_nodeadmin.model.TreeNode'
});