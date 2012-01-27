Ext.define('subjectadmin.view.dashboard.Dashboard' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.dashboard',
    cls: 'dashboard sidebarlayout',

    layout: 'border',

    items: [{
        xtype: 'container',
        cls: 'centercolumn',
        region: 'center',
        items: [{
            xtype: 'actionlist',
            data: {
                title: 'Actions',
                links: [{
                    url: '#/@@create-new-assignment/@@chooseperiod',
                    text: 'Create new assignment'
                }, {
                    url: '#/',
                    text: 'Browse all'
                }, {
                    url: '#/@@register-for-final-exams',
                    text: 'Register students that qualify for final exams'
                }, {
                    url: '#/@@global-statistics',
                    text: 'Statistics'
                }]
            }
        }, {
            xtype: 'box',
            cls: 'sysadmin-messages box',
            html: [
                '<h2 class="boxtitle">Information from Drift</h2>',
                '<div class="boxbody">',
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
        border: 'false',
        region: 'east',
        width: 400,
        cls: 'sidebarcolumn',
        items: [{
            xtype: 'shortcutlist'
        }]
    }]
});
