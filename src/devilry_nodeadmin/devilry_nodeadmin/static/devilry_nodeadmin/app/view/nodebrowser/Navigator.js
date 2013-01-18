Ext.define('devilry_nodeadmin.view.nodebrowser.Navigator', {
    extend: 'Ext.view.View',
    alias: 'widget.navigator',
    cls: 'devilry_nodeadmin_navigator bootstrap',

    store: 'NodeDetails',

    tpl: [
        '<tpl for=".">',
            '<div>',
            '<span>{ short_name }</span>',
            '<tpl if="predecessor">',
                '<a href="/devilry_nodeadmin/#/node/"><i class="icon-home"></i>',
                    gettext( 'to the top' ),
                '</a>',
                '<a href="/devilry_nodeadmin/#/node/{ predecessor.id }"><i class="icon-chevron-up"></i>',
                    gettext( 'up' ),
                '</a>',
            '<tpl else>',
                '<a href="/devilry_nodeadmin/#/node/"><i class="icon-home"></i>',
                    gettext( 'to the top' ),
                '</a>',
            '</tpl>',
            '</div>',
        '</tpl>',
        '<hr />'
    ],

    itemSelector: ''

});