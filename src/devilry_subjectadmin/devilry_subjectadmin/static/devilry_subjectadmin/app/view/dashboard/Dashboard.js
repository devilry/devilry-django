Ext.define('devilry_subjectadmin.view.dashboard.Dashboard' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.dashboard',
    cls: 'dashboard',

    layout: 'column',
    frame: false,
    border: 0,
    bodyPadding: 40,
    autoScroll: true,

    items: [{
        xtype: 'container',
        columnWidth: .65,
        items: [{
            xtype: 'panel',
            title: pgettext('subjectadmin dashboard', 'Active subjects'),
            ui: 'inset-header-strong-panel',
            items: {
                xtype: 'shortcutlist'
            }
        }]
    }, {
        xtype: 'container',
        columnWidth: .35,
        margin: '0 0 0 40',
        border: false,
        items: [{
            xtype: 'panel',
            title: pgettext('subjectadmin dashboard', 'Messages'),
            ui: 'lookslike-parawitheader-panel',
            cls: 'bootstrap',
            html: [
                '<p>Please use the help-tab to access guides and tips. Contact ',
                'drift@example.com if anything is unclear.</p>',
                '<p><strong>Note:</strong> Devilry will be taken down for scheduled maintainance at ',
                '24. may from  16:00 to 18:00. Please let us know if this is a ',
                'bad time, and we will consider re-scheduling the maintainance.',
            ].join('')
        }]
    }]
});
