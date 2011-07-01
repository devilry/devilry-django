Ext.define('devilry.administrator.MultiNodeGridSearchField', {
    extend: 'Ext.form.field.Text',
    alias: 'widget.devilry-administrator-multistoresearchfield',

    initComponent: function() {
        Ext.apply(this, {
            fieldLabel: 'Search',
            renderTo: 'searchfield',
            width: 500,
            //triggerAfterChars: 1,

            listeners: {
                specialKey: function(field, e) {
                    if(e.getKey() == e.ENTER) {
                        Ext.each(this.resultgrids, function(grid, index, resultgrids) {
                            var store = grid.store;
                            store.proxy.extraParams.query = field.getValue();
                            store.load();
                        });
                    }
                }
            }
        });
        this.callParent(arguments);
    },
});
