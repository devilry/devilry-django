Ext.define('devilry.restful.model.Assignment', {
    extend: 'Ext.data.Model',
    belongsTo: 'devilry.restful.model.Period',
    fields: [
        {name:'id', type:'int'},
        {name:'short_name', type:'string'},
        {name:'long_name', type:'string'},
        {name:'path', type:'string'},
        {name:'parentnode__short_name', type:'string'},
        {name:'parentnode__parentnode__long_name', type:'string'},
        {name:'parentnode__parentnode__short_name', type:'string'}
    ],
    idProperty: 'id'
});
