Ext.define('devilry.statistics.SidebarPluginContainer', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.statistics-sidebarplugincontainer',
    layout: 'accordion',

    constructor: function(config) {
        this.callParent([config]);
    },

    initComponent: function() {
        this.items = [];
        Ext.each(this.sidebarplugins, function(sidebarplugin, index) {
            var plugin = Ext.create(sidebarplugin, {
                loader: this.loader,
                aggregatedStore: this.aggregatedStore
            });
            this.items.push(plugin);
        }, this);
        this.callParent(arguments);
    }
});
