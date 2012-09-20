Ext.define('devilry_subjectadmin.view.guidesystem.GuideView', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.guidesystemview',
    cls: 'devilry_subjectadmin_guidesystemview bootstrap',

    layout: 'anchor',
    title: gettext('Loading') + ' ...',
    bodyPadding: 10,
    closable: true,
    closeAction: 'hide',
    items: [{
        xtype: 'box',
        itemId: 'progress',
        cls: 'guidesystem_progress',
        tpl: [
            '<p>',
                gettext('Step {current} of {total}'),
            '</p>'
        ]
    }, {
        xtype: 'container',
        layout: 'fit',
        itemId: 'body'
    }]
});
