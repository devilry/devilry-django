Ext.define('devilry_header.model.StudentSearchResult', {
    extend: 'Ext.data.Model',

    idProperty: 'id',
    fields: [
        {name: 'id', type: 'int'},
        {name: 'path', type: 'string'},
        {name: 'title',  type: 'string'},
        {name: 'name',  type: 'string'},
        {name: 'students',  type: 'auto'},
        {name: 'type',  type: 'string'}
    ],

    proxy: {
        type: 'rest',
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_search/rest/studentcontent',
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
