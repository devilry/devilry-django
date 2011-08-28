Ext.define('devilry.extjshelpers.PermissionChecker', {
    extend: 'Ext.Component',
    hidden: true,
    config: {
        stores: [],
        emptyHtml: undefined
    },

    constructor: function(config) {
        this.callParent([config]);
        this.loadedItems = 0;
        this.loadedWithRecords = 0;

        Ext.each(this.stores, function(store, index) {
            store.on('load', this.onLoadStore, this);
        }, this);
    },

    onLoadStore: function(store) {
        this.loadedItems ++;
        if(store.totalCount > 0) {
            this.loadedWithRecords ++;
        }
        if(this.loadedItems === this.stores.length) {
            this.fireEvent('allLoaded', this.loadedItems, this.loadedWithRecords);
            if(this.loadedWithRecords === 0) {
                this.fireEvent('noPermission', this.loadedItems, this.loadedWithRecords);
                this.update(this.emptyHtml);
                this.show();
            } else {
                this.fireEvent('hasPermission', this.loadedItems, this.loadedWithRecords);
            }
        }
    }
});
