Ext.define('devilry.statistics.AggregatedPeriodDataModel', {
    extend: 'Ext.data.Model',

    idProperty: 'userid',
    fields: [
        {name: 'userid',  type: 'int'},
        {name: 'user',  type: 'auto'},
        {name: 'relatedstudent',  type: 'auto'},
        {name: 'groups',  type: 'auto'}
    ],

    proxy: {
        type: 'rest',
        urlpatt: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_qualifiesforexam/rest/aggregatedperiod/{0}',
        url: null, // Set dynamically using ``urlpatt``
        extraParams: {
            format: 'json'
        },
        reader: {
            type: 'json'
        }
    }
});
