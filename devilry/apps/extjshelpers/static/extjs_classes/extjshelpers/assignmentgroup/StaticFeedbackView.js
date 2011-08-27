Ext.define('devilry.extjshelpers.assignmentgroup.StaticFeedbackView', {
    extend: 'devilry.extjshelpers.SingleRecordView',
    alias: 'widget.staticfeedbackview',
    cls: 'widget-staticfeedbackview',

    tpl: Ext.create('Ext.XTemplate',
        '<tpl if="!isactive">',
        '   <section class="warning-small">',
        '       <h1>This is not the active feedback</h1>',
        '       When an examiner publish a feedback, the feedback is ',
        '       stored forever. When an examiner needs to modify a feedback, ',
        '       they create a new feedback. Therefore, you see more than ',
        '       one feedback in the toolbar above. Unless there is something ',
        '       wrong with the latest feedback, you should not have to ',
        '       read this feedback',
        '   </section>',
        '</tpl>',

        '<section class="{gradecls}">',
        '   <h1>Grade</h1>',
        '       <p>',
        '       <tpl if="!is_passing_grade">',
        '           The given grade, <strong>{grade}</strong>, is <strong>not</strong> a passing grade.',
        '       </tpl>',
        '       <tpl if="is_passing_grade">',
        '           The given grade, <strong>{grade}</strong>, is a passing grade.',
        '       </tpl>',
        '       This feedback was published <em>{save_timestamp:date}</em>.',
        '       </p>',
        '</section>',
        '<section class="rendered_view">{rendered_view}<section>'
    ),

    
    getData: function(data) {
        data.gradecls = data.is_passing_grade? 'ok-small': 'error-small';
        return data;
    },
});
