Ext.define('devilry.restful.model.Subject', {
    extend: 'Ext.data.Model',
    hasMany: {model: 'devilry.restful.model.Period', name: 'periods'},
    idProperty: 'path', // Since we use this in a tree, we need something that is unique in the entire tree (which 'id' is not)
    fields: [
        {name:'id', type:'int'},
        {name:'path', type:'string'},
        {name:'short_name', type:'string'},
        {name:'long_name', type:'string'}
    ]
    //idProperty: 'id'
});
