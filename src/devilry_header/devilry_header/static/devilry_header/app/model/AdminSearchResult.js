Ext.define('devilry_header.model.AdminSearchResult', {
    extend: 'Ext.data.Model',

    idProperty: 'id',
    fields: [
        {name: 'id', type: 'int'},
        {name: 'path', type: 'string'},
        {name: 'title',  type: 'string'},
        {name: 'type',  type: 'string'}
    ],

    proxy: {
        type: 'rest',
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_search/rest/admincontent',
        extraParams: {
            format: 'json'
        },
        reader: {
            type: 'json'
        }
    }
});
