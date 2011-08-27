/** A button bar containing {@link devilry.extjshelpers.ButtonBarButton} many.
 *
 * Add buttons as items to the container.
 * */
Ext.define('devilry.extjshelpers.ButtonBar', {
    extend: 'Ext.container.Container',
    requires: ['devilry.extjshelpers.ButtonBarButton'],
    alias: 'widget.buttonbar',
    border: 0,
    height: 40,
    layout: {
        type: 'hbox',
        align: 'stretch',
        pack: 'center'
    },

    config: {
        emptyHtml: undefined,
    },

    constructor: function(config) {
        this.loadedItems = 0;
        this.loadedWithRecords = 0;
        this.initConfig(config);
        this.callParent([config]);
    },

    initComponent: function() {
        this.callParent(arguments);
        this.on('render', this.updateMask, this);
    },

    updateMask: function() {
        if(this.loadedItems == this.items.items.length) {
            this.getEl().unmask();
            if(this.loadedWithRecords == 0) {
                this.height = 'auto';
                this.update(this.emptyHtml);
            };
        } else {
            this.getEl().mask('Loading...');
        }
    },

    notifyStoreLoad: function(hasRecords) {
        this.loadedItems ++;
        if(hasRecords) {
            this.loadedWithRecords ++;
        }
        this.updateMask();
    }
});
