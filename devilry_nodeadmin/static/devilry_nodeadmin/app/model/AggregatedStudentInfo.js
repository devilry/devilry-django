Ext.define('devilry_nodeadmin.model.AggregatedStudentInfo', {
    extend: 'Ext.data.Model',

    fields: [
        {name: 'user', type: 'auto'},
        {name: 'grouped_by_hierarky', type: 'auto'}
    ],

    proxy: {
        type: 'rest',
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_nodeadmin/rest/aggregatedstudentinfo/',

        headers: {
            'Accept': 'application/json'
        },

        reader: {
            type: 'json'
        }
    }
});
