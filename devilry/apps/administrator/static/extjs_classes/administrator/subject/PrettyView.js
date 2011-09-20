Ext.define('devilry.administrator.subject.PrettyView', {
    extend: 'devilry.administrator.PrettyView',
    alias: 'widget.administrator_subjectprettyview',

    bodyTpl: Ext.create('Ext.XTemplate',
        '<div class="section help">',
        '    <h1>What is a subject?</h1>',
        '    <p>',
        '        A subject is usually a course or seminar. A subject contains periods, which are usually semesters.',
        '    </p>',
        '</section>'
    )
});
