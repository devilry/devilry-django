Ext.define('subjectadmin.view.dashboard.Dashboard' ,{
    extend: 'Ext.container.Container',
    alias: 'widget.dashboard',
    cls: 'dashboard sidebarlayout',
    requires: [
        'themebase.layout.RightSidebar'
    ],

    layout: 'rightsidebar',
    frame: false,

    items: [{
        xtype: 'container',
        cls: 'centercolumn',
        region: 'main',
        items: [{
            xtype: 'container',
            cls: 'centerbox',
            items: [{
                xtype: 'box',
                html: Ext.String.format('<h2 class="centertitle">{0}</h2>', dtranslate('subjectadmin.dashboard.actionstitle')),
            }, {
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
            xtype: 'box',
            cls: 'sysadmin-messages centerbox',
            html: [
                '<h2 class="centertitle">Information from Drift</h2>',
                '<div class="centerbody">',
                '    <p>Please use the help-tab to access guides and tips. Contact ',
                '    drift@example.com if anything is unclear.</p>',
                '    <p><strong>Note:</strong> Devilry will be taken down for scheduled maintainance at ',
                '    24. mai from  16:00 to 18:00. Please let us know if this is a ',
                '    bad time, and we will consider re-scheduling the maintainance.',
                '</div>'
            ].join(''),
        }]
    }, {
        xtype: 'container',
        border: false,
        region: 'sidebar',
        items: [{
            xtype: 'shortcutlist'
        }]
    }]
});
