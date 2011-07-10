/** A textfield for searching.
 *
 * @xtype administratormultisearchfield
 * */
Ext.define('devilry.administrator.MultiSearchField', {
    extend: 'Ext.form.field.Text',
    alias: 'widget.administratormultisearchfield',

    initComponent: function() {
        var me = this;
        Ext.apply(this, {
            width: 600,
            fieldStyle: {
                'font-size': '30px',
                'line-height': 'normal',
                'height': 'auto',
                'padding': '7px',
                'border-radius': '15px'
            },
            emptyText: 'Search for anything...',

            listeners: {
                specialKey: function(field, e) {
                    if(e.getKey() == e.ENTER) {
                        me.ownerCt.search(me.getValue());
                    } else if(e.getKey() == e.ESC) {
                        me.ownerCt.hideResults();
                    }
                },

                /* TODO: Wait for 0.2 sec or something before searhing on change. */
                change: function(field, newValue, oldValue) {
                    me.ownerCt.search(newValue);
                }
            }
        });
        this.callParent(arguments);
    }
});
