Ext.define('devilry.extjshelpers.assignmentgroup.StaticFeedbackView', {
    extend: 'devilry.extjshelpers.SingleRecordView',
    alias: 'widget.staticfeedbackview',
    cls: 'widget-staticfeedbackview',

    tpl: Ext.create('Ext.XTemplate',
        '<tpl if="!isactive">',
        '   <div class="warning">',
        '       <strong>This is not the active feedback.</strong>',
        '       When an examiner publish a feedback, the feedback is ',
        '       stored forever. When an examiner needs to modify a feedback, ',
        '       they create a new feedback. Therefore, you see more than ',
        '       one feedback in the menu above. Unless there is something ',
        '       wrong with the latest feedback, you should not have to ',
        '       read this feedback',
        '   </div>',
        '</tpl>',
        '<div class="rendered_view">{rendered_view}<div>'
    )
});
