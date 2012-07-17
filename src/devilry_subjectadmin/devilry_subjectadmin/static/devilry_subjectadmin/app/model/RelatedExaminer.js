Ext.define('devilry_subjectadmin.model.RelatedExaminer', {
    extend: 'Ext.data.Model',
    idProperty: 'id',
    fields: [
        {name: 'id', type: 'int'},
        {name: 'period',  type: 'int'},
        {name: 'user',  type: 'auto'}
    ],

    proxy: {
        type: 'rest',
        urlpatt: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_subjectadmin/rest/relatedexaminer/{0}/',
        url: null, // We use baseurl to dynamically set the url from urlpatt
        extraParams: {
            format: 'json'
        },
        reader: {
            type: 'json'
        }
    }
});
