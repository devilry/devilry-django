Ext.define('devilry_subjectadmin.view.guidesystem.GuideView', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.guidesystemview',
    cls: 'devilry_subjectadmin_guidesystemview bootstrap',
    ui: 'helpsidebar',

    requires: [
        'devilry_extjsextras.AlertMessage'
    ],

    title: gettext('Loading') + ' ...',
    bodyPadding: 0,
    closable: true,
    closeAction: 'hide',
    layout: 'card',
    overflowY: 'auto',
    items: [{
        xtype: 'container',
        itemId: 'main',
        layout: 'anchor',
        items: [{
            xtype: 'box',
            itemId: 'progress',
            cls: 'guidesystem_progress',
            tpl: gettext('Step {current} of {total}')
        }, {
            xtype: 'container',
            padding: Ext.isIE? '10 30 10 10': 10,
            layout: 'fit',
            itemId: 'body'
        }]
    }, {
        xtype: 'alertmessage',
        type: 'error',
        margin: 10,
        itemId: 'invalidPageMessage',
        title: gettext('Invalid guide step'),
        message: gettext('The current guide does not recognize this page. Please use your browser back button to return to the previous page, and read the instructions one more time.')
    }]
});
