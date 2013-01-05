Ext.define('devilry_qualifiesforexam.view.selectplugin.ListPlugins' ,{
    extend: 'Ext.view.View',
    alias: 'widget.listplugins',
    cls: 'devilry_qualifiesforexam_listplugins bootstrap',

    store: 'Plugins',
    tpl: [
        '<ul class="unstyled">',
            '<tpl for=".">',
                '<li class="plugininfo">',
                    '<strong><a href="{url}">{title}</a></strong>',
                    '<p class="muted"><small>{description}</small></p>',
                '</li>',
            '</tpl>',
        '</ul>'
    ],
    itemSelector: 'li.plugininfo',
    emptyText: gettext('No plugins available')
});
