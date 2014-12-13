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
            interpolate(gettext( 'These are only the nodes you control. Select an element to see the child levels, its %(subjects_term)s and %(periods_term)s.' ), {
                subjects_term: gettext('subjects'),
                periods_term: gettext('periods')
             }, true),
        '</p>'
    ],

    itemSelector: 'a.node'

});
