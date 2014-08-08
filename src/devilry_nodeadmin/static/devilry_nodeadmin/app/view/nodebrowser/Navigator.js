Ext.define('devilry_nodeadmin.view.nodebrowser.Navigator', {
    extend: 'Ext.Component',
    alias: 'widget.navigator',
    cls: 'devilry_nodeadmin_navigator bootstrap',

    tpl: [
        '<div>',
            '<tpl if="predecessor">',
                '<a href="/devilry_nodeadmin/#/node/" class="homelink"><i class="icon-home"></i>',
                    gettext( 'to the top' ),
                '</a>',
                '<a href="/devilry_nodeadmin/#/node/{ predecessor.id }" class="uplink"><i class="icon-chevron-up"></i>',
                    gettext( 'up' ),
                '</a>',
            '<tpl else>',
                '<a href="/devilry_nodeadmin/#/node/"><i class="icon-chevron-up"></i>',
                    gettext( 'up' ),
                '</a>',
            '</tpl>',
        '</div>'
    ]
});
