Ext.define('devilry.statistics.dataview.BaseView', {
    extend: 'Ext.container.Container',
    layout: 'fit',
    config: {
        loader: undefined
    },
    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },

    initComponent: function() {
        this.callParent(arguments);
        this.refresh();
    }
});
