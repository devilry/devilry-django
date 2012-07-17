Ext.define('devilry_subjectadmin.model.RelatedExaminer', {
    extend: 'devilry_subjectadmin.model.RelatedUserBase',
    idProperty: 'id',
    fields: [
        {name: 'id', type: 'int'},
        {name: 'period',  type: 'int'},
        {name: 'tags',  type: 'string'},
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
