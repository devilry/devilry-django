Ext.define('devilry_subjectadmin.model.AllWhereIsAdmin', {
    extend: 'Ext.data.Model',

    idProperty: 'id',
    fields: [
        {name: 'id', type: 'int'},
        {name: 'can_administer', type: 'bool'},
        {name: 'is_admin', type: 'bool'},
        {name: 'short_name',  type: 'string'},
        {name: 'long_name',  type: 'string'},
        {name: 'periods',  type: 'auto'}
    ],

    proxy: {
        type: 'rest',
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_subjectadmin/rest/allwhereisadmin/',
        extraParams: {
            format: 'json'
        },
        reader: {
            type: 'json'
        }
    }
});
