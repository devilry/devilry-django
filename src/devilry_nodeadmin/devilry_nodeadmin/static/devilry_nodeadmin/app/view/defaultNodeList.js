Ext.define('devilry_nodeadmin.view.defaultNodeList', {
    extend: 'Ext.view.View',
    alias: 'widget.defaultnodelist',
    cls: 'primary',
    tpl: [
        '<div class="bootstrap">',
            '<tpl for=".">',
                '<div class="bootstrap node" style="padding-bottom: 10px;">',
                '<a href="/devilry_nodeadmin/#/node/{ id }"><h3>{ long_name }</h3>',
                '<tpl if="most_recent_start_time != null">',
                    '<div>Earliest start time: { most_recent_start_time }</div>',
                '<tpl else>',
                    '<div>Earliest start time: none</div>',
                '</tpl>',
                '</a>',
                '</div>',
            '</tpl>',
            '<div class="footer">Denne listen viser kun de nodene du administrerer. Klikk på et element for å se ',
            'de underliggende nivåene, emnene og periodene. Du kan gå ett nivå tilbake ved hjelp av knappen ',
            'i det øvre høyre hjørne.</div>',
        '</div>'
    ],

    itemSelector: 'div.node',

    initComponent: function() {
        this.store = Ext.create( 'devilry_nodeadmin.store.RelatedNodes' );
        this.callParent(arguments);
    }

});