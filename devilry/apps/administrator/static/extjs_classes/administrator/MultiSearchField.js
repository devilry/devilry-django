/** A textfield for searching and reloading multiple stores.
 *
 * @xtype administratormultisearchfield
 * */
Ext.define('devilry.administrator.MultiSearchField', {
    extend: 'Ext.form.field.Text',
    alias: 'widget.administratormultisearchfield',

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

    /** Get the result container, which we expect to be the second item in the
     * ownerCt. */
    getResultContainer: function() {
        return this.ownerCt.items.items[1];
    },

    
    /** Search for the current value in the stores in all items in the
     * container returned by getResultContainer(). */
    search: function() {
        var me = this;
        Ext.each(this.getResultContainer().items.items, function(grid, index, resultgrids) {
            var store = grid.store;
            store.proxy.extraParams.query = me.getValue();
            store.load();
        });
    }
});
