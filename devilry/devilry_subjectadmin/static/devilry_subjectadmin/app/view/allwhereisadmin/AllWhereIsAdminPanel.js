Ext.define('devilry_subjectadmin.view.allwhereisadmin.AllWhereIsAdminPanel' ,{
    extend: 'Ext.container.Container',
    alias: 'widget.allwhereisadminpanel', // Define the widget xtype as allwhereisadminpanel
    cls: 'dashboard',

    requires: [
        'devilry_subjectadmin.view.allwhereisadmin.AllWhereIsAdminList'
    ],

    layout: 'anchor',
    frame: false,
    border: 0,
    padding: '20 40 20 40',
    autoScroll: true,

    items: [{
        xtype: 'box',
        cls: 'bootstrap',
        anchor: '100%',
        html: [
            '<h1 style="margin-top: 0;">',
                gettext('All my courses'),
            '</h1>',
            '<p class="muted">',
                gettext('These are all courses, terms and assignments where you have administrator rights. Assignments are included in the listing if you have administrator-rights on the assignment, and not on the terms or courses containing the assignment. The courses name is a link if you have administrator rights on the courses.'),
            '</p>'
        ].join('')
    }, {
        xtype: 'container',
        border: 1,
        padding: '10 20 10 20',
        anchor: '100%',
        layout: 'fit',
        cls: 'devilry_focuscontainer',
        items: {
            xtype: 'allwhereisadminlist'
        }
    }]
});
