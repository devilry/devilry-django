Ext.define('devilry_subjectadmin.view.guidesystem.GuideList', {
    extend: 'Ext.Component',
    alias: 'widget.guidesystemlist',

    tpl: [
        '<tpl if="guides">',
            '<ul>',
            '<tpl for="guides">',
                '<li><p>',
                    '<a href="#" data-guidename="name">',
                '</p></li>',
            '</tpl>',
            '</ul>',
        '</tpl>'
    ]
});
