Ext.define('devilry_nodeadmin.view.defaultNodeList', {
    extend: 'Ext.view.View',
    alias: 'widget.defaultnodelist',
    cls: 'bootstrap',
    tpl: [
        '<div class="bootstrap">',
            '<small>Denne listen viser kun nodene der du er administrator. Klikk på elementene for å se',
                ' de underliggende nodene, og bruk tilbakeknappen for å gå en node opp i hierarkiet.</small>',
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