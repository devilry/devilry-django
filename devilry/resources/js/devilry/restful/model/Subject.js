Ext.define('devilry.restful.model.Subject', {
    extend: 'Ext.data.Model',
    fields: [
        {name: 'id', type:'string'},
        {name: 'short_name', type:'string'},
        {name: 'long_name', type:'string'}
    ]
    //idProperty: 'id'
});
