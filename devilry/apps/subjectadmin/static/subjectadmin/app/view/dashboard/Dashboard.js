Ext.define('subjectadmin.view.dashboard.Dashboard' ,{
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
            cls: 'centerbox',
            title: dtranslate('subjectadmin.dashboard.actionstitle'),
            ui: 'inset-header-strong-panel',
            items: [{
                xtype: 'actionlist',
                cls: 'centerbody',
                links: [{
                    url: '#/@@create-new-assignment/@@chooseperiod',
                    text: dtranslate('subjectadmin.dashboard.createnewassignment')
                }, {
                    url: '#/',
                    text: dtranslate('subjectadmin.dashboard.browseall')
                }, {
                    url: '#/@@register-for-final-exams',
                    text: dtranslate('subjectadmin.dashboard.registerqualifiesforfinal')
                }, {
                    url: '#/@@global-statistics',
                    text: dtranslate('subjectadmin.dashboard.overview-and-statistics')
                }]
            }]
        }, {
            xtype: 'panel',
            margin: {top: 40},
            title: dtranslate('subjectadmin.dashboard.shortcuts'),
            ui: 'inset-header-panel',
            items: {
                xtype: 'shortcutlist'
            }
        }]
    }, {
        xtype: 'container',
        columnWidth: .35,
        margin: {left: 40},
        border: false,
        items: [{
            xtype: 'panel',
            title: dtranslate('subjectadmin.dashboard.messages'),
            ui: 'lookslike-parawitheader-panel',
            cls: 'bootstrap',
            html: [
                '<p>Please use the help-tab to access guides and tips. Contact ',
                'drift@example.com if anything is unclear.</p>',
                '<p><strong>Note:</strong> Devilry will be taken down for scheduled maintainance at ',
                '24. mai from  16:00 to 18:00. Please let us know if this is a ',
                'bad time, and we will consider re-scheduling the maintainance.',
            ].join(''),
        }]
    }]
});
