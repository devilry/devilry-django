Ext.define('devilry_subjectadmin.view.dashboard.Dashboard' ,{
    extend: 'Ext.container.Container',
    alias: 'widget.dashboard',
    cls: 'dashboard',

    requires: [
        'devilry_subjectadmin.view.dashboard.AllActiveWhereIsAdminList'
    ],

    layout: 'column',
    padding: '40',
    autoScroll: true,

    items: [{
        xtype: 'container',
        columnWidth: 1,
        cls: 'devilry_focuscontainer',
        padding: '20',
        items: [{
            xtype: 'allactivewhereisadminlist'
        }, {
            xtype: 'box',
            cls: 'bootstrap',
            margin: '40 0 0 0',
            html: [
                '<h2 style="font-size:20px; margin-bottom:4px; line-height:1;">',
                    gettext('Expired courses'),
                '</h2>',
                '<p style="margin-top: 0px; padding-top: 0;">',
                    '<a href="#/">',
                        gettext('Browse everything where you are administrator'),
                    '</a>',
                '</p>'
            ].join('')
        }]
    }, {
        xtype: 'container',
        width: 250,
        margin: '10 0 0 50',
        border: false,
        layout: 'anchor',
        items: [{
            xtype: 'box',
            cls: 'bootstrap',
            tpl: '<h4>{heading}</h4>',
            data: {
                heading: gettext('Interractive guides')
            }
        }, {
            xtype: 'guidesystemlist',
            guides: [{
                xtype: 'guide-createnewassignment',
                title: gettext('Create new assignment'),
                description: gettext('Takes you through creating any kind of assignment (electronic, paper, exam, ...).')
            }, {
                xtype: 'guide-qualifiedforfinalexams',
                title: gettext('Qualified for final exams'),
                description: gettext('Takes you through selecting students that qualify for final exams.')
            }]
        }, {
            xtype: 'box',
            cls: 'bootstrap',
            tpl: [
                '<h4>{heading}</h4>',
                '<p class="muted"><small>',
                    gettext('Click the question-mark button in the header.'),
                '</small></p>'
            ],
            data: {
                heading: gettext('More guides and help')
            }
        }]
    }]
});
