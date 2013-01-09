Ext.define('devilry_qualifiesforexam.view.selectplugin.ListPlugins' ,{
    extend: 'Ext.view.View',
    alias: 'widget.listplugins',
    cls: 'devilry_qualifiesforexam_listplugins bootstrap',

    /**
     * @cfg {int} [periodid]
     */

    store: 'Plugins',
    tpl: [
        '<ul class="unstyled">',
            '<tpl for="items">',
                '<li class="plugininfo">',
                    '<strong><a href="{url}?periodid={parent.periodid}&pluginsessionid={pluginsessionid}">{title}</a></strong>',
                    '<p class="muted"><small>{description}</small></p>',
                '</li>',
            '</tpl>',
        '</ul>'
    ],
    itemSelector: 'li.plugininfo',
    emptyText: gettext('No plugins available'),

    collectData : function(records, startIndex){
        var dataArray = this.callParent(arguments);
        return {
            items: dataArray,
            periodid: this.periodid
        };
//        return dataArray;
    }
});
