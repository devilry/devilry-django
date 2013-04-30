Ext.define('devilry_nodeadmin.view.nodebrowser.NodeChildrenList', {
    extend: 'Ext.Component',
    alias: 'widget.nodechildrenlist',
    cls: 'devilry_nodeadmin_nodechildrenlist bootstrap',

    tpl: [
        '<tpl if="nodes.length">',
            '<ul class="unstyled">',
                '<tpl for="nodes">',
                    '<li>',
                        '<a href="/devilry_nodeadmin/#/node/{ id }">{ long_name }</a>',
                    '</li>',
                '</tpl>',
            '</ul>',
        '<tpl else>',
            '<p class="muted no_nodes_on_level">', gettext('No child-nodes on this level'), '</p>',
        '</tpl>',
        {
            formatDatetime: function(datetime) {
                return devilry_extjsextras.DatetimeHelpers.formatDateTimeShort(datetime);
            }
        }
    ]
});
