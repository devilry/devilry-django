Ext.define('devilry_nodeadmin.view.defaultNodeList', {
    extend: 'Ext.view.View',
    alias: 'widget.defaultnodelist',
    cls: 'bootstrap',
    tpl: [
        '<div class="bootstrap">',
            '<h1>Node browser</h1>',
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