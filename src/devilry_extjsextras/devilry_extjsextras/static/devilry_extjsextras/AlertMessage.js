/**
Message for highlighting the failure, possible failure, or success of
an action. Particularly useful for forms.
*/ 
Ext.define('devilry_extjsextras.AlertMessage', {
    extend: 'Ext.Component',
    alias: 'widget.alertmessage',
    
    tpl: [
        '<div class="alert alert-{type}">',
            '<tpl if="closable">',
                '<button type="button" class="close" data-dismiss="alert">×</button>',
            '</tpl>',
            '<tpl if="title">',
                '<strong>{title}</strong>',
            '</tpl>',
            '{message}',
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


    /**
     * @cfg {bool} [closable=false]
     * Show close button. The ``closed`` event is fired when the button is
     * clicked.
     */
    closable: false,

    /**
     * @cfg
     * An optional title for the message.
     */
    title: null,

    initComponent: function() {
        var cls = 'bootstrap devilry_extjsextras_alertmessage';
        if(this.cls) {
            cls += Ext.String.format('{0} {1}', cls, this.cls);
        }
        this.cls = cls;
        this.callParent(arguments);
        this.update(this.message, this.type);

        this.addListener({
            scope: this,
            element: 'el',
            delegate: '.close',
            click: function(e) {
                e.preventDefault();
                this.fireEvent('closed', this, e);
            }
        });
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
            message: this.message,
            title: this.title,
            closable: this.closable
        }]);
    }
});
