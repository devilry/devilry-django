Ext.define('devilry.administrator.MultiNodeGridSearchField', {
    extend: 'Ext.form.field.Text',
    alias: 'widget.administrator-multistoresearchfield',

    initComponent: function() {
        Ext.apply(this, {
            fieldLabel: 'Search',
            renderTo: 'searchfield',
            width: 600,
            //triggerAfterChars: 1,

            listeners: {
                specialKey: function(field, e) {
                    if(e.getKey() == e.ENTER) {
                        Ext.each(this.resultContainer.items.items, function(grid, index, resultgrids) {
                            var store = grid.store;
                            store.proxy.extraParams.query = field.getValue();
                            store.load();
                        });
                    }
                }
            }
        });
        this.callParent(arguments);
    }
});
