Ext.define('devilry.extjshelpers.assignmentgroup.StaticFeedbackView', {
    extend: 'devilry.extjshelpers.SingleRecordView',
    alias: 'widget.staticfeedbackview',
    cls: 'widget-staticfeedbackview',

    tpl: Ext.create('Ext.XTemplate',
        '<div class="bootstrap">',
            '<tpl if="!isactive">',
                '<div class="alert">',
                    '<h4>This is not the active feedback</h4>',
                    'When an examiner publish a feedback, the feedback is ',
                    'stored forever. When an examiner needs to modify a feedback, ',
                    'they create a new feedback. Therefore, you see more than ',
                    'one feedback in the toolbar above. Unless there is something ',
                    'wrong with the latest feedback, you should not have to ',
                    'read this feedback',
                '</div>',
            '</tpl>',

            '<div class="alert alert-{gradecls}">',
                '<strong>', gettext('Grade'), '</strong>: ',
                '{is_passing_grade_label} ({grade})',
            '</div>',

            '<div class="rendered_view_preview">{rendered_view}</div>',
        '</div>'
    ),

    
    getData: function(data) {
        data.gradecls = data.is_passing_grade? 'success': 'warning';
        data.is_passing_grade_label = data.is_passing_grade? gettext('Passed'): gettext('Failed');
        return data;
    }
});
