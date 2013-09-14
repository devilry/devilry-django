Ext.define('devilry_nodeadmin.model.AggregatedStudentInfoModel', {
    extend: 'Ext.data.Model',

    fields: [
        {name: 'user', type: 'int'},
        {name: 'user', type: 'auto'},
        {name: 'display_name', type: 'string'},
        {name: 'full_name', type: 'string'},
        {name: 'email', type: 'string'}
    ],

    proxy: {
        type: 'rest',
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_nodeadmin/rest/aggregatedstudentinfo/12',
        extraParams: {
            format: 'json'
        },
        reader: {
            type: 'json'
        }
    }
});
