/** A textfield for searching.
 *
 * @xtype multisearchfield
 * */
Ext.define('devilry.extjshelpers.searchwidget.MultiSearchField', {
    extend: 'Ext.form.field.Text',
    alias: 'widget.multisearchfield',

    config: {
        /**
         * @cfg
         * Delay before a search is performed in milliseconds. Defaults to 300.
         * The search is not performed if the user changes the input text before
         * ``searchdelay`` is over.
         */
        searchdelay: 300
    },

    initComponent: function() {
        var me = this;
        Ext.apply(this, {
            width: 600,
            fieldCls: 'searchfield',
            emptyText: 'Search for anything...',

            listeners: {
                specialKey: function(field, e) {
                    me.handleSpecialKey(e);
                },

                change: function(field, newValue, oldValue) {
                    me.handleChange(newValue);
                }
            }
        });
        this.callParent(arguments);
    },

    searchIfLatest: function(value) {
        var currentValue = this.getValue();
        if(value == currentValue) {
            this.ownerCt.search(value);
        }
    },

    handleSpecialKey: function(e) {
        if(e.getKey() == e.ENTER) {
            this.ownerCt.search(this.getValue());
        } else if(e.getKey() == e.ESC) {
            this.ownerCt.hideResults();
        }
    },

    handleChange: function(newValue) {
        if(Ext.String.trim(newValue) == "") {
            this.ownerCt.hideResults();
        } else {
            var me = this;
            Ext.Function.defer(function() {
                me.searchIfLatest(newValue);
            }, this.searchdelay);
        }
    }
});
