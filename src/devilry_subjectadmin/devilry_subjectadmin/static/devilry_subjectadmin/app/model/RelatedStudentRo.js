Ext.define('devilry_subjectadmin.model.RelatedStudentRo', {
    extend: 'devilry_subjectadmin.model.RelatedStudent',

    proxy: {
        type: 'rest',
        urlpatt: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_subjectadmin/rest/relatedstudent_assignment_ro/{0}/',
        url: null, // We use baseurl to dynamically set the url from urlpatt
        extraParams: {
            format: 'json'
        },
        reader: {
            type: 'json'
        }
    }
});
