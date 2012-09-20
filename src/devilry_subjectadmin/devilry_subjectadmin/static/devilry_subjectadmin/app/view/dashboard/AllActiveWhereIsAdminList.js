Ext.define('devilry_subjectadmin.view.dashboard.AllActiveWhereIsAdminList' ,{
    extend: 'Ext.Component',
    alias: 'widget.allactivewhereisadminlist',
    cls: 'devilry_subjectadmin_allactivewhereisadminlist bootstrap',
    tpl: [
        '<tpl if="loadingtext">',
            '<h2>{loadingtext}</h2>',
        '<tpl else>',
            '<h1>',
                interpolate(gettext('Active %(periods_term)s'), {
                    periods_term: gettext('periods')
                }, true),
            '</h1>',
            '<p class="muted">',
                interpolate(gettext('These are your %(subjects_term)s with an active %(period_term)s. Choose a %(period_term)s to create new %(assignments_term)s, manage existing %(assignments_term)s and much more.'), {
                    subjects_term: gettext('subjects'),
                    period_term: gettext('period'),
                    assignments_term: gettext('assignments'),
                    assignment_term: gettext('assignment')
                }, true),
            '</p>',
            '<ul class="unstyled">',
            '<tpl for="subjects">',
                //'<p class="subject subject_{data.short_name}">',
                    //'{[Ext.String.ellipsis(values.data.long_name, 40)]}',
                //'</p>',
                '<tpl for="data.periods">',
                    '<tpl exec="values.subject = parent.data;"></tpl>',
                    '<li>',
                        '<tpl if="can_administer">',
                            '<p><strong><a href="#/period/{id}/">',
                                '{subject.short_name} - ',
                                '{[Ext.String.ellipsis(values.long_name, 40)]}',
                            '</a></strong></p>',
                        '<tpl else>',
                            '<tpl for="assignments">',
                                '<li><p><strong><a href="#/assignment/{id}/">',
                                    '{parent.subject.short_name} - ',
                                    '{parent.short_name} - ',
                                    '{[Ext.String.ellipsis(values.long_name, 40)]}',
                                '</a></strong></p></li>',
                            '</tpl>',
                        '</tpl>',
                    '</li>',
                '</tpl>',
                '</ul>',
            '</tpl>',
            '</ul>',
        '</tpl>'
    ],

    data: {
        loadingtext: gettext('Loading') + ' ...'
    }
});
