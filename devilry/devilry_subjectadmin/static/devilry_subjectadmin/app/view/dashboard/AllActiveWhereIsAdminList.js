Ext.define('devilry_subjectadmin.view.dashboard.AllActiveWhereIsAdminList' ,{
    extend: 'Ext.Component',
    alias: 'widget.allactivewhereisadminlist',
    cls: 'devilry_subjectadmin_allactivewhereisadminlist bootstrap',
    tpl: [
        '<tpl if="loadingtext">',
            '<h1 style="margin-top: 0;">',
                '{loadingtext}',
            '</h1>',
        '<tpl else>',
            '<h1 style="margin-top: 0;">',
                gettext('Active courses'),
            '</h1>',
            '<ul class="unstyled">',
                '<tpl for="list">',
                    '<li>',
                        '<p>',
                            '<strong><a href="#/{type}/{id}/">',
                                '{text}',
                            '</a></strong>',
                            '<tpl if="suffix">',
                                '<small class="muted"> - {suffix}</small>',
                            '</tpl>',
                        '</p>',
                    '</li>',
                '</tpl>',
            '</ul>',
        '</tpl>'
    ],

    data: {
        loadingtext: gettext('Loading') + ' ...'
    }
});
