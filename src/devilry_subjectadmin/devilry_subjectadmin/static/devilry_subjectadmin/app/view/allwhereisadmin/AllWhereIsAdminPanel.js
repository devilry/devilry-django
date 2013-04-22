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
                interpolate(gettext('All my %(subjects_term)s'), {
                    subjects_term: gettext('subjects')
                }, true),
            '</h1>',
            '<p class="muted">',
                interpolate(gettext('These are all %(subjects_term)s, %(periods_term)s and assignments where you have administrator rights. Assignments are included in the listing if you have administrator-rights on the assignment, and not on the %(period_term)s or %(subject_term)s containing the assignment. The %(subject_term)s name is a link if you have administrator rights on the %(subject_term)s.'), {
                    subjects_term: gettext('subjects'),
                    periods_term: gettext('periods'),
                    subject_term: gettext('subject'),
                    period_term: gettext('period')
                }, true),
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
