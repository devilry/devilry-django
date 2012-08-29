Ext.define('devilry_subjectadmin.view.dashboard.Dashboard' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.dashboard',
    cls: 'dashboard',

    requires: [
        'devilry_subjectadmin.view.AllWhereIsAdminList'
    ],

    layout: 'column',
    frame: false,
    border: 0,
    bodyPadding: 40,
    autoScroll: true,

    items: [{
        xtype: 'container',
        columnWidth: .65,
        items: [{
            xtype: 'allwhereisadminlist'
        }, {
            xtype: 'box',
            cls: 'bootstrap',
            margin: '40 0 0 0',
            html: [
                '<h2>',
                    interpolate(gettext('Inactive %(subjects_term)s and old data'), {
                        subjects_term: gettext('subjects')
                    }, true),
                '</h2>',
                '<p>',
                    '<a href="#/doesnotexist">',
                        gettext('Browse everything where you are administrator'),
                    '</a>',
                '</p>'
            ].join('')
        }]
    }, {
        xtype: 'container',
        columnWidth: .35,
        margin: '0 0 0 40',
        border: false,
        items: [{
            xtype: 'box',
            html: '&nbsp;'
        }]
    }]
});
