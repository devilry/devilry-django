Ext.define('devilry_subjectadmin.model.ExaminerStat', {
    extend: 'Ext.data.Model',

    idProperty: 'id',
    fields: [
        {name: 'id', type: 'int'},
        {name: 'examiner', type: 'auto'},
        {name: 'waitingfordeliveries_count', type: 'int'},
        {name: 'waitingforfeedback_count', type: 'int'},
        {name: 'nodeadlines_count', type: 'int'},
        {name: 'closedwithoutfeedback_count', type: 'int'},
        {name: 'failed_count', type: 'int'},
        {name: 'passed_count', type: 'int'},
        {name: 'corrected_count', type: 'int'},
        {name: 'groups', type: 'auto'}
    ],

    proxy: {
        type: 'rest',
        urlpatt: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_subjectadmin/rest/examinerstats/{0}',
        url: null,
        extraParams: {
            format: 'json'
        },
        reader: {
            type: 'json'
        },

        setUrl: function(assignment_id) {
            this.url = Ext.String.format(this.urlpatt, assignment_id);
        }
    }
});
