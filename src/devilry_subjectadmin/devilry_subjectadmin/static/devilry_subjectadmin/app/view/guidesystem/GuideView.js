Ext.define('devilry_subjectadmin.view.guidesystem.GuideView', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.guidesystemview',
    cls: 'devilry_subjectadmin_guidesystemview bootstrap',

    requires: [
        'devilry_extjsextras.AlertMessage'
    ],

    title: gettext('Loading') + ' ...',
    bodyPadding: 10,
    closable: true,
    closeAction: 'hide',
    layout: 'card',
    items: [{
        xtype: 'container',
        itemId: 'main',
        layout: 'anchor',
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
    }, {
        xtype: 'alertmessage',
        type: 'error',
        itemId: 'invalidPageMessage',
        title: gettext('Invalid guide step'),
        message: gettext('The current guide does not recognize this page. Please use your browser back button to return to the previous page, and read the instructions one more time.')
    }]
});
