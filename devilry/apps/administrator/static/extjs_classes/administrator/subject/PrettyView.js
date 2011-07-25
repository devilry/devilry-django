Ext.define('devilry.administrator.subject.PrettyView', {
    extend: 'devilry.administrator.PrettyView',
    alias: 'widget.administrator_subjectprettyview',

    bodyTpl: Ext.create('Ext.XTemplate',
        '<section>',
        '<p>What should we put here?</p>',
        '</section>'
    )
});
