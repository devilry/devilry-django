/**
One-line messages for highlighting the failure, possible failure, or success of
an action. Particularly useful for forms.
*/ 
Ext.define('themebase.AlertMessage', {
    extend: 'Ext.Component',
    alias: 'widget.alertmessage',
    
    tpl: [
        '<div class="alert-message {type}">',
        '  <p>{message}</p>',
        '</div>'
    ],

    /**
     * @cfg
     * Type of message. Valid values: 'error', 'warning', 'info' or 'success'.
     * Defaults to 'warning'.
     */
    type: 'warning',

    /**
     * @cfg
     * The one line of message to display. This is not required, as it may be
     * useful to initialize an hidden alert message and use update() to change
     * the message when there is a message to show.
     */
    message: '',

    initComponent: function() {
        this.callParent(arguments);
        this.update(this.message, this.type);
    },

    /**
     * Update the message and optionally the type. If the type is not
     * specified, the type will not be changed.
     * */
    update: function(message, type) {
        if(type) {
            this.type = type;
        }
        this.message = message;
        this.callParent([{
            type: this.type,
            message: this.message
        }]);
    }
});
