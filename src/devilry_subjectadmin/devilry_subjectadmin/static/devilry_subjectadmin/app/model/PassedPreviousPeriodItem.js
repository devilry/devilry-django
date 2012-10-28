Ext.define('devilry_subjectadmin.model.PassedPreviousPeriodItem', {
    extend: 'Ext.data.Model',
    idProperty: 'id',
    fields: [
        {name: 'id', type: 'int'},
        {name: 'group', type: 'auto'},
        {name: 'oldgroup', type: 'auto', persist: false},
        {name: 'whyignored', type: 'string', persist: false},
        {name: 'feedback', type: 'auto'},
        {name: 'grade', type: 'text', persist: false},
        {name: 'comment', type: 'text', persist: false}
    ],

    proxy: {
        type: 'rest',
        urlpatt: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_subjectadmin/rest/passedinpreviousperiod/{0}',
        url: null, // We use urlpatt to dynamically generate the url
        batchActions: true,
        appendId: false, 
        extraParams: {
            format: 'json'
        },
        reader: {
            type: 'json'
        }
    }
});
