Ext.define('devilry_subjectadmin.model.DetailedPeriodOverview', {
    extend: 'Ext.data.Model',
    fields: [
        {name: 'students_with_feedback_that_is_candidate_but_not_in_related', type: 'auto'},
        {name: 'students_with_no_feedback_that_is_candidate_but_not_in_related', type: 'auto'},
        {name: 'relatedstudents', type: 'auto'},
        {name: 'assignments', type: 'auto'}
    ],

    proxy: {
        type: 'rest',
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_subjectadmin/rest/detailedperiodoverview/',
        extraParams: {
            format: 'json'
        },
        reader: {
            type: 'json'
        }
    }
});
