Ext.define('devilry_nodeadmin.view.dashboard.DefaultNodeList', {
    extend: 'Ext.view.View',
    alias: 'widget.defaultnodelist',
    cls: 'devilry_nodeadmin_defaultnodelist bootstrap',

    store: 'RelatedNodes',

    tpl: [
        '<ul class="unstyled devilry_nodeadmin_massive_navlist">',
            '<tpl for=".">',
                '<li>',
                    '<a href="/devilry_nodeadmin/#/node/{ id }">{ long_name }</a>',
                '</li>',
            '</tpl>',
        '</ul>',
        '<p class="muted">',
            interpolate(gettext( 'These are only the nodes you control. Select an element to see the child levels, its %(subjects_term)s and %(periods_term)s.' ), {
                subjects_term: gettext('subjects'),
                periods_term: gettext('periods')
             }, true),
        '</p>'
    ],

    itemSelector: 'a.node'

});
