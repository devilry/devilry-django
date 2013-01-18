Ext.define('devilry_subjectadmin.model.ExaminerStat', {
    extend: 'Ext.data.Model',

    idProperty: 'id',
    fields: [
        {name: 'id', type: 'int'},
        {name: 'examiner', type: 'auto'},
        {name: 'waitingfordeliveries', type: 'auto'},
        {name: 'waitingforfeedback', type: 'auto'},
        {name: 'nodeadlines', type: 'auto'},
        {name: 'closedwithoutfeedback', type: 'auto'},
        {name: 'failed', type: 'auto'},
        {name: 'passed', type: 'auto'}
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
