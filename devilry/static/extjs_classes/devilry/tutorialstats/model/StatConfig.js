Ext.define('devilry.tutorialstats.model.StatConfig', {
    extend: 'Ext.data.Model',
    fields: [
        {name:'id', type:'int'},
        {name:'name', type:'string'},
        {name:'period__id', type:'int'},
        {name:'user__id', type:'int'}
    ],
    idProperty: 'id'
});
