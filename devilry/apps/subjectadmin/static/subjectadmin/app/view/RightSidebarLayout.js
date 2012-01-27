Ext.define('subjectadmin.view.RightSidebarLayout', {
    alias: ['layout.rightsidebar'],
    extend: 'Ext.layout.container.Border',


    /** Class added to the container using this layout. */
    markerCls: 'sidebarlayout',

    /** Each item in the container will have their attributes overridden by
     * these values.  The value chosen is based on their ``region`` setting. */
    regionMap: {
        'main': {
            region: 'center',
            cls: 'centercolumn'
        },
        'sidebar': {
            region: 'east',
            cls: 'sidebarcolumn'
        },
    },

    getLayoutItems: function() {
        var items = this.callParent(arguments);
        this.owner.addClass('sidebarlayout');

        // Map of regions
        var i = 0;
        for (; i < items.length; i++) {
            var config = items[i];
            var attrs = this.regionMap[config.region];
            if(!attrs) {
                throw Ext.String.format(
                    "Invalid region: {0}. Must be one of: {1}",
                    config.region,
                    Ext.Object.getKeys(regionMap).join(', ')
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
