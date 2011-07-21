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
         * Delay before a search is performed in milliseconds. Defaults to 500.
         * The search is not performed if the user changes the input text before
         * ``searchdelay`` is over.
         */
        searchdelay: 500
    },

    constructor: function(config) {
        this.callParent([config]);
        this.initConfig(config);
        this.addEvents('emptyInput');
        this.addEvents('newInput');
    },

    initComponent: function() {
        var me = this;
        Ext.apply(this, {
            width: 600,
            fieldCls: 'searchfield',
            emptyText: 'Search for anything...',

            listeners: {
                scope: this,
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

    triggerSearch: function(value) {
        var currentValue = this.getValue();
        var noNewInput = value == currentValue;
        if(noNewInput) {
            if(Ext.String.trim(currentValue) == "") {
                this.ownerCt.hideResults();
            } else {
                console.log(value);
                this.ownerCt.search(value);
            }
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
        var me = this;
        Ext.Function.defer(function() {
            me.triggerSearch(newValue);
        }, this.searchdelay);
    }
});
