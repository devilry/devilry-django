Ext.define('devilry_subjectadmin.view.allwhereisadmin.AllWhereIsAdminList' ,{
    extend: 'Ext.Component',
    alias: 'widget.allwhereisadminlist',
    cls: 'devilry_subjectadmin_allwhereisadminlist bootstrap',
    tpl: [
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
                        '<a href="#/period/{id}/">',
                            '{[Ext.String.ellipsis(values.long_name, 40)]}',
                        '</a>',
                        '</li>',
                    '<tpl else>',
                        '<tpl for="assignments">',
                            '<li><a href="#/assignment/{id}/">',
                                '{parent.short_name} - ',
                                '{[Ext.String.ellipsis(values.long_name, 40)]}',
                            '</a></li>',
                        '</tpl>',
                    '</tpl>',
                '</tpl>',
            '</ul>',
        '</tpl>'
    ],

    data: {
        subjects: []
    }
});
