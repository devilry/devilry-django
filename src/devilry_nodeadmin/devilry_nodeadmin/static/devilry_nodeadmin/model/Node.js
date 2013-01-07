Ext.define( 'devilry_nodeadmin.model.Node', {
    extend: 'Ext.data.Model',
    idProperty: 'id',
    fields: [
        {name: 'id',  type: 'int'},
	{short_name: 'short_name', type: 'string'},
	{long_name: 'long_name', type: 'string'}
    ]
});