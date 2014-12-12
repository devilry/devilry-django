Ext.define('devilry_subjectadmin.model.AllActiveWhereIsAdmin', {
    extend: 'devilry_subjectadmin.model.AllWhereIsAdmin',

    proxy: {
        type: 'rest',
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_subjectadmin/rest/allwhereisadmin/',
        extraParams: {
            format: 'json',
            only_active: 'yes' // NOTE: This is the only difference from the AllWhereIsAdmin model
        },
        reader: {
            type: 'json'
        }
    }
});
