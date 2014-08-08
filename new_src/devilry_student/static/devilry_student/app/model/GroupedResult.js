Ext.define('devilry_student.model.GroupedResult', {
    extend: 'Ext.data.Model',

    idProperty: 'id',
    fields: [
        {name: 'id', type: 'int'},
        {name: 'short_name', type: 'string'},
        {name: 'long_name', type: 'string'},
        {name: 'periods', type: 'auto'}
    ],

    proxy: {
        type: 'rest',
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_student/rest/results-grouped',
        extraParams: {
            format: 'json'
        },
        reader: {
            type: 'json'
        }
    }
});
