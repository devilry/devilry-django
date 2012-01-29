/**
A container of AlerMessages. This container is perfect for top-of-form
messages. It defaults to beeing hidden. When you add a message it
becomes invisible, and when you remove all messages, it hides itself
automatically.
*/ 
Ext.define('themebase.AlertMessageList', {
    extend: 'Ext.panel.Panel',
    requires: [
        'themebase.AlertMessage'
    ],
    ui: 'transparentpanel',
    alias: 'widget.alertmessagelist',
    hidden: true,

    constructor: function() {
        var config = {
            listeners: {
                scope: this,
                remove: this._onRemove
            }
        };
        this.callParent([config]);
    },

    /** Create and add a ``themebase.AlertMessage``. The config parameter is
     * forwarded to the AlertMessage constructor. */
    add: function(config) {
        this.callParent([Ext.widget('alertmessage', config)]);
        this.show();
    },
    
    _onRemove: function() {
        var messages = this.query('alertmessage');
        if(messages.length === 0) {
            this.hide();
        }
    },

    /** Add many messages of the same type.
     *
     * @param messages Array of messages (strings).
     * @param type The type of the message (see ``themebase.AlertMessage.type``).
     * */
    addMany: function(messages, type) {
        Ext.Array.each(messages, function(message) {
            this.add({
                message: message,
                type: type
            });
        }, this);
    }
});
