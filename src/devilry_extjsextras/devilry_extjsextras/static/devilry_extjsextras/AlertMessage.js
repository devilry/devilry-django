/**
Message for highlighting the failure, possible failure, or success of
an action. Particularly useful for forms.
*/ 
Ext.define('devilry_extjsextras.AlertMessage', {
    extend: 'Ext.Component',
    alias: 'widget.alertmessage',

    requires: [
        'Ext.fx.Animator'
    ],
    
    tpl: [
        '<div class="alert alert-{type}" style="{style}">',
            '<tpl if="closable">',
                '<button type="button" class="close" data-dismiss="alert">×</button>',
            '</tpl>',
            '<tpl if="title">',
                '<strong>{title}</strong>: ',
            '</tpl>',
            '{message}',
        '</div>'
    ],

    /**
     * @cfg {String} [boxMargin]
     * Override the margin style of the alert DIV.
     */
    boxMargin: undefined,

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
     * @cfg {int} [autoclose]
     * Fire the ``close`` event ``autoclose`` seconds after creating the message.
     * If ``true``, we calculate the autoclose time automatically based on the
     * number of words.
     */

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
                this.fireEvent('closed', this);
            }
        });

        if(!Ext.isEmpty(this.autoclose)) {
            if(this.autoclose === true) {
                this.autoclose = this._calculateAutocloseTime();
            }
            Ext.defer(function() {
                this.fadeOutAndClose();
            }, 1000*this.autoclose, this);
        }
    },

    _calculateAutocloseTime: function() {
        var alltext = this.message;
        if(!Ext.isEmpty(this.title)) {
            alltext += this.title;
        }
        var words = Ext.String.splitWords(alltext);
        var sec = words.length * 0.4; // One second per work
        sec = sec > 3? sec: 3; // ... but never less than 3 sec
        return Math.round(2 + sec); // 2 seconds to focus on the message + time to read it
    },

    fadeOutAndClose: function() {
        Ext.create('Ext.fx.Animator', {
            target: this.getEl(),
            duration: 3000,
            keyframes: {
                0: {
                    opacity: 1,
                },
                100: {
                    opacity: 0.1,
                }
            },
            listeners: {
                scope: this,
                afteranimate: function() {
                    this.fireEvent('closed', this);
                }
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
        var style = '';
        if(!Ext.isEmpty(this.boxMargin)) {
            style = Ext.String.format('margin: {0};', this.boxMargin);
        }
        this.callParent([{
            type: this.type,
            message: this.message,
            title: this.title,
            style: style,
            closable: this.closable
        }]);
    }
});
