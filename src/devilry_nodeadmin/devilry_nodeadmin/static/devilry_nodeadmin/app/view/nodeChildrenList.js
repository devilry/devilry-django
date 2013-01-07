Ext.define('devilry_nodeadmin.view.nodeChildrenList', {
    extend: 'Ext.view.View',
    alias: 'widget.nodechildrenlist',
    cls: 'nodechildrenlist',
    tpl: [
        '<div class="bootstrap">',
        '<h1>Contains</h1>',
            '<tpl for=".">',
            '<div class="bootstrap node" style="padding-bottom: 10px;">',
                '<a href="/devilry_nodeadmin/#/node/{ id }"><h3>',
                    '<tpl for="parent">{ short_name }</tpl>',
                ' / { long_name }</h3>',
                '<tpl if="most_recent_start_time != null">',
                    '<div>Earliest start time: { most_recent_start_time }</div>',
                '<tpl else>',
                    '<div>Earliest start time: none</div>',
                '</tpl>',
                '</a>',
            '</div>',
            '</tpl>',
            '<div style="padding-top: 20px;"><a href="">&lt; back to the top level</a></div>',
        '</div>'
    ],

    itemSelector: 'div.node',

    initComponent: function() {
        this.store = Ext.create( 'devilry_nodeadmin.store.NodeChildren' );
        this.store.proxy.url = Ext.String.format('/devilry_nodeadmin/rest/node/{0}', this.node_pk );
        this.callParent(arguments);
    }

});