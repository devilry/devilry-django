Ext.define('devilry.extjshelpers.assignmentgroup.StaticFeedbackView', {
    extend: 'devilry.extjshelpers.SingleRecordView',
    alias: 'widget.staticfeedbackview',
    cls: 'widget-staticfeedbackview',

    tpl: Ext.create('Ext.XTemplate',
        '<tpl if="is_passing_grade">',
        '    <section class="ok-small">',
        '       <h1>Passing grade</h1>',
        '       <p>The given grade is a passing grade.</p>',
        '    </section>',
        '</tpl>',
        '<tpl if="!is_passing_grade">',
        '    <section class="error-small">',
        '       <h1>Failing grade</h1>',
        '       <p>The given grade is <strong>not</strong> a passing grade.</p>',
        '    </section>',
        '</tpl>',

        '<section class="info-small">',
        '   <h1>Grade</h1>',
        '   <p><em>{grade}</em></p>',
        '</section>',

        '<section class="info-small">',
        '   <h1>Feedback publish time</h1>',
        '   <p>This feedback was published <em>{save_timestamp:date}</em></p>',
        '</section>',

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
        '<section class="rendered_view">{rendered_view}<section>'
    )
});
