Ext.define('devilry_subjectadmin.model.RelatedExaminerRo', {
    extend: 'devilry_subjectadmin.model.RelatedExaminer',

    proxy: {
        type: 'rest',
        urlpatt: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_subjectadmin/rest/relatedexaminer_assignment_ro/{0}/',
        url: null, // We use baseurl to dynamically set the url from urlpatt
        extraParams: {
            format: 'json'
        },
        reader: {
            type: 'json'
        }
    }
});
