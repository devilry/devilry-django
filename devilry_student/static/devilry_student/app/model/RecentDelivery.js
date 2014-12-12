Ext.define('devilry_student.model.RecentDelivery', {
    extend: 'Ext.data.Model',

    idProperty: 'id',
    fields: [
        {name: 'id', type: 'int'},
        {name: 'group', type: 'auto'},
        {name: 'assignment', type: 'auto'},
        {name: 'period', type: 'auto'},
        {name: 'subject', type: 'auto'},
        {name: 'time_of_delivery', type: 'auto'},
        {name: 'number', type: 'int'}
    ],

    proxy: {
        type: 'rest',
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_student/rest/recent-deliveries/',
        extraParams: {
            format: 'json'
        },
        reader: {
            type: 'json'
        }
    }
});
