Ext.define('devilry_nodeadmin.model.AggregatedStudentInfoModel', {
    extend: 'Ext.data.Model',

    fields: [
        {name: 'user', type: 'auto'}
    ],

    proxy: {
        type: 'rest',
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_nodeadmin/rest/aggregatedstudentinfo/12',

      headers: {
        'Accept': 'application/json'
      },
      
        extraParams: {
            format: 'json'
        },
        reader: {
            type: 'json'
        }
    }
});
