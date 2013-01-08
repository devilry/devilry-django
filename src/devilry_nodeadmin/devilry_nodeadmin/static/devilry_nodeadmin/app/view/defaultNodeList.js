Ext.define('devilry_nodeadmin.view.defaultNodeList', {
    extend: 'Ext.view.View',
    alias: 'widget.defaultnodelist',
    cls: 'primary',
    tpl: [
        '<div class="bootstrap">',
            '<small>Denne listen viser kun de nodene du administrerer. Klikk på elementene for å se',
                ' de underliggende nivå, og bruk tilbakeknappen for å gå et nivå opp i hierarkiet.</small>',
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
        '</div>'
    ],

    itemSelector: 'div.node',

    initComponent: function() {
        this.store = Ext.create( 'devilry_nodeadmin.store.RelatedNodes' );
        this.callParent(arguments);
    }

});