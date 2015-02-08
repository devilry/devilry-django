Ext.define('devilry_nodeadmin.view.dashboard.ToplevelNodeList', {
    extend: 'Ext.view.View',
    alias: 'widget.toplevelnodelist',
    cls: 'devilry_nodeadmin_toplevelnodelist bootstrap',

    store: 'ToplevelNodes',

    tpl: [
        '<ul class="unstyled devilry_nodeadmin_massive_navlist">',
            '<tpl for=".">',
                '<li>',
                    '<a href="/devilry_nodeadmin/#/node/{ id }">{ long_name }</a>',
                '</li>',
            '</tpl>',
        '</ul>',
        '<p class="muted">',
            gettext( 'These are only the nodes you control. Select an element to see the child levels, its courses and periods.' ),
        '</p>'
    ],

    itemSelector: 'a.node'

});
