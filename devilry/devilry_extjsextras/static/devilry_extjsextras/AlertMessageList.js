/**
A container of AlerMessages. This container is perfect for top-of-form
messages. It defaults to beeing hidden. When you add a message it
becomes invisible, and when you remove all messages, it hides itself
automatically.
*/ 
Ext.define('devilry_extjsextras.AlertMessageList', {
    extend: 'Ext.panel.Panel',
    requires: [
        'devilry_extjsextras.AlertMessage'
    ],
    alias: 'widget.alertmessagelist',
    hidden: true,
    frame: false,
    border: false,
    bodyStyle: 'background-color: transparent !important;',

    layout: 'anchor',

    initComponent: function() {
        if(Ext.isEmpty(this.cls)) {
            this.cls = [];
        } else {
            this.cls = Ext.toArray();
        }
        this.cls.push('devilry_extjsextras_alertmessagelist');
        this.on('remove', this._onRemove, this);
        this.callParent(arguments);
        this.addListener({
            scope: this,
            closed: this.onClose
        });
    },

    onClose: function(alertmessage) {
        this.remove(alertmessage, true);
    },

    /** Create and add a ``devilry_extjsextras.AlertMessage``. The config parameter is
     * forwarded to the AlertMessage constructor. */
    add: function(config) {
        var messageConfig = {};
        Ext.apply(messageConfig, this.messageDefaults);
        Ext.apply(messageConfig, config);
        var message = Ext.widget('alertmessage', messageConfig);
        this.callParent([message]);
        message.enableBubble('closed');
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
     * @param type The type of the message (see ``devilry_extjsextras.AlertMessage.type``).
     * */
    addMany: function(messages, type) {
        Ext.Array.each(messages, function(message) {
            this.add({
                message: message,
                type: type
            });
        }, this);
    },

    /** Add many messages by array.
     *
     * Functionally the same as looping over ``configs``, and calling ``add()``
     * for each config.
     *
     * @param configs Array of configuration objects for ``add()``.
     * */
    addArray: function(configs) {
        Ext.Array.each(configs, function(config) {
            this.add(config);
        }, this);
    }
});
