Ext.define('devilry.restful.model.Assignment', {
    extend: 'Ext.data.Model',
    fields: [
        'id',
        'short_name',
        'long_name',
        'path',
        'parentnode__short_name',
        'parentnode__parentnode__long_name',
        'parentnode__parentnode__short_name'
    ],
    idProperty: 'id'
});
