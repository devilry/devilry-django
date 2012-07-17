Ext.define('devilry_subjectadmin.model.RelatedStudent', {
    extend: 'Ext.data.Model',
    idProperty: 'id',
    fields: [
        {name: 'id', type: 'int'},
        {name: 'period',  type: 'int'},
        {name: 'candidate_id',  type: 'string'},
        {name: 'user',  type: 'auto'}
    ],

    proxy: {
        type: 'rest',
        urlpatt: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_subjectadmin/rest/relatedstudent/{0}/',
        url: null, // We use baseurl to dynamically set the url from urlpatt
        extraParams: {
            format: 'json'
        },
        reader: {
            type: 'json'
        }
    }
});
