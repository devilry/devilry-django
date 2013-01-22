Ext.define('devilry_header.model.AdminSearchResult', {
    extend: 'Ext.data.Model',

    idProperty: 'id',
    fields: [
        {name: 'id', type: 'int'},
        {name: 'path', type: 'string'},
        {name: 'title',  type: 'string'},
        {name: 'name',  type: 'string'},
        {name: 'students',  type: 'auto'},
        {name: 'assignment_id',  type: 'auto'},
        {name: 'type',  type: 'string'}
    ],

    proxy: {
        type: 'rest',
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_search/rest/admincontent',
        extraParams: {
            format: 'json'
        },
        reader: {
            type: 'json',
            root: 'matches',
            totalProperty: 'total'
        }
    }
});
