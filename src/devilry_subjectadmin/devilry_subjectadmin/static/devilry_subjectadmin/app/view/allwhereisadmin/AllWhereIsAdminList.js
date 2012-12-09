Ext.define('devilry_subjectadmin.view.allwhereisadmin.AllWhereIsAdminList' ,{
    extend: 'Ext.Component',
    alias: 'widget.allwhereisadminlist',
    cls: 'devilry_subjectadmin_allwhereisadminlist bootstrap',
    tpl: [
        '<tpl if="loadingtext">',
            '<h2>{loadingtext}</h2>',
        '<tpl else>',
            '<h1>',
                interpolate(gettext('All %(subjects_term)s'), {
                    subjects_term: gettext('subjects')
                }, true),
            '</h1>',
            '<p class="muted">',
                interpolate(gettext('These are all %(subjects_term)s, %(periods_term)s and assignments where you have administrator rights. Assignments are listed if you have administrator-rights on the assignments, and not on the %(period_term)s or %(subject_term)s containing the assignment. The %(subject_term)s name is a link on if you have administrator rights on the subject.'), {
                    subjects_term: gettext('subjects'),
                    periods_term: gettext('periods'),
                    subject_term: gettext('subject'),
                    period_term: gettext('period')
                }, true),
            '</p>',
            '<tpl for="subjects">',
                '<h3 class="subject subject_{data.short_name}">',
                    '<tpl if="data.can_administer">',
                        '<a href="#/subject/{data.id}/">',
                            '{data.long_name}',
                        '</a>',
                    '<tpl else>',
                        '{data.long_name}',
                    '</tpl>',
                '</h3>',
                    '<ul class="unstyled">',
                    '<tpl for="data.periods">',
                        '<tpl if="can_administer">',
                            '<li>',
                            '<p><strong><a href="#/period/{id}/">',
                                '{[Ext.String.ellipsis(values.long_name, 40)]}',
                            '</a></strong></p>',
                            '</li>',
                        '<tpl else>',
                            '<tpl for="assignments">',
                                '<li><p><strong><a href="#/assignment/{id}/">',
                                    '{parent.short_name} - ',
                                    '{[Ext.String.ellipsis(values.long_name, 40)]}',
                                '</a></strong></p></li>',
                            '</tpl>',
                        '</tpl>',
                    '</tpl>',
                '</ul>',
            '</tpl>',
        '</tpl>'
    ],

    data: {
        loadingtext: gettext('Loading') + ' ...'
    }
});
