Ext.define('devilry_nodeadmin.view.DefaultNodeList', {
    extend: 'Ext.view.View',
    alias: 'widget.defaultnodelist',
    cls: 'primary',
    tpl: [
        '<h1>Navigér</h1>',
        '<hr />',
        '<tpl for=".">',
            '<div class="bootstrap node" style="padding-bottom: 10px;">',
                '<a href="/devilry_nodeadmin/#/node/{ id }"><h3>{ long_name }</h3></a>',
            '</div>',
        '</tpl>',
        '<div class="footer">Denne listen viser kun de nodene du administrerer. Klikk på et element for å se ',
        'de underliggende nivåene, emnene og periodene. Du kan gå ett nivå tilbake ved hjelp av knappen ',
        'i det øvre høyre hjørne.</div>'
    ],

    itemSelector: 'div.node',

    initComponent: function() {
        this.store = Ext.create( 'devilry_nodeadmin.store.RelatedNodes' );
        this.callParent(arguments);
    }

});