Ext.define('themebase.layout.RightSidebar', {
    alias: ['layout.rightsidebar'],
    extend: 'Ext.layout.container.Border',


    /** Class added to the container using this layout. */
    markerCls: 'rightsidebarlayout',

    /** Each item in the container will have their attributes overridden by
     * these values.  The value chosen is based on their ``region`` setting. */
    regionMap: {
        'main': {
            region: 'center',
            cls: 'centercolumn',
            border: 'false'
        },
        'sidebar': {
            region: 'east',
            cls: 'sidebarcolumn',
            border: 'false',
            width: 400
        },
    },

    getLayoutItems: function() {
        var items = this.callParent(arguments);
        this.owner.addClass(this.markerCls);

        // Map of regions
        var i = 0;
        for (; i < items.length; i++) {
            var config = items[i];
            var attrs = this.regionMap[config.region];
            if(!attrs) {
                throw Ext.String.format(
                    "Invalid region: {0}. Must be one of: {1}",
                    config.region,
                    Ext.Object.getKeys(this.regionMap).join(', ')
                );
            }
            var cls = attrs.cls;
            if(config.cls) {
                cls += ' ' + config.cls;
            }
            Ext.apply(config, attrs);
            config.cls = cls;
        }

        return items;
    },
});
