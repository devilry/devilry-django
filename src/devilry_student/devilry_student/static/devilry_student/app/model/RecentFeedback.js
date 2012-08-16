Ext.define('devilry_student.model.RecentFeedback', {
    extend: 'Ext.data.Model',

    idProperty: 'id',
    fields: [
        {name: 'id', type: 'int'},
        {name: 'group', type: 'auto'},
        {name: 'assignment', type: 'auto'},
        {name: 'period', type: 'auto'},
        {name: 'subject', type: 'auto'},
        {name: 'number', type: 'int'},
        {name: 'last_feedback', type: 'auto'}
    ],

    proxy: {
        type: 'rest',
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_student/rest/recent-feedbacks/',
        extraParams: {
            format: 'json'
        },
        reader: {
            type: 'json'
        }
    }
});
