Ext.define('devilry.restful.model.Period', {
    extend: 'Ext.data.Model',
    belongsTo: 'devilry.restful.model.Subject',
    idProperty: 'path', // Since we use this in a tree, we need something that is unique in the entire tree (which 'id' is not)
    fields: [
        {name:'id', type:'int'},
        {name:'path', type:'string'},
        {name:'short_name', type:'string'},
        {name:'long_name', type:'string'}
    ]
    //idProperty: 'id'
});
