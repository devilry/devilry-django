/** User search model. */
Ext.define('devilry_usersearch.UserSearchModel', {
    extend: 'Ext.data.Model',

    idProperty: 'id',
    fields: [
        {name: 'id',  type: 'int'},
        {name: 'username',  type: 'string'},
        {name: 'full_name',  type: 'string'},
        {name: 'email',  type: 'string'},
        {name: 'languagecode',  type: 'string'}
    ],

    proxy: {
        type: 'rest',
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_usersearch/search',
        extraParams: {
            format: 'json'
        },
        reader: {
            type: 'json'
        }
    }
});
