Ext.define('devilry_qualifiesforexam.model.Plugin', {
    extend: 'Ext.data.Model',

    idProperty: 'id',
    fields: [
        {name: 'id', type: 'string'},
        {name: 'title',  type: 'string'},
        {name: 'description', type: 'string'},
        {name: 'pluginsessionid', type: 'string'},
        {name: 'url', type: 'string'}
    ],

    proxy: {
        type: 'rest',
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_qualifiesforexam/rest/plugins',
        extraParams: {
            format: 'json'
        },
        reader: {
            type: 'json'
        }
    }
});
