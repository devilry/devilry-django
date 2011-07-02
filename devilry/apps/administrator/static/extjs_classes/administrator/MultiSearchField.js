/**
 * A textfield for searching and reloading multiple stores. */
Ext.define('devilry.administrator.MultiSearchField', {
    extend: 'Ext.form.field.Text',
    alias: 'widget.administrator-multisearchfield',

    initComponent: function() {
        var me = this;
        Ext.apply(this, {
            fieldLabel: 'Search',
            renderTo: 'searchfield',
            width: 600,
            //triggerAfterChars: 1,

            listeners: {
                specialKey: function(field, e) {
                    if(e.getKey() == e.ENTER) {
                        me.search();
                    }
                },

                /* TODO: Wait for 0.2 sec or something before searhing on change. */
                change: function(field, newValue, oldValue) {
                    me.search();
                }
            }
        });
        this.callParent(arguments);
    },

    
    /** Search in the stores in all items in the ``resultContainer``. */
    search: function() {
        var me = this;
        Ext.each(this.resultContainer.items.items, function(grid, index, resultgrids) {
            var store = grid.store;
            store.proxy.extraParams.query = me.getValue();
            store.load();
        });
    }
});
