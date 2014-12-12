Ext.define('devilry_student.model.FindGroup', {
    extend: 'Ext.data.Model',

    idProperty: 'id',
    fields: [
        {name: 'id', type: 'int'},
        {name: 'name', type: 'string'},
        {name: 'assignment', type: 'auto'},
        {name: 'period', type: 'auto'},
        {name: 'subject', type: 'auto'}
    ],

    proxy: {
        type: 'rest',
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_student/rest/find-groups/',
        extraParams: {
            format: 'json'
        },
        reader: {
            type: 'json'
        }
    }
});
