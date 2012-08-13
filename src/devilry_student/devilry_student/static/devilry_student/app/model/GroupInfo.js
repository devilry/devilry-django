Ext.define('devilry_student.model.GroupInfo', {
    extend: 'Ext.data.Model',

    idProperty: 'id',
    fields: [
        {name: 'id',  type: 'int'},
        {name: 'name',  type: 'string'},
        {name: 'is_open',  type: 'bool'},
        {name: 'candidates',  type: 'auto'},
        {name: 'deadlines',  type: 'auto'}
    ],

    proxy: {
        type: 'rest',
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_student/rest/aggregated_groupinfo',
        extraParams: {
            format: 'json'
        },
        reader: {
            type: 'json'
        }
    }
});
