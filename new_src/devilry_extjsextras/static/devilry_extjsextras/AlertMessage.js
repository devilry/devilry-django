/**
Message for highlighting the failure, possible failure, or success of
an action. Particularly useful for forms.
*/ 
Ext.define('devilry_extjsextras.AlertMessage', {
    extend: 'devilry_extjsextras.MarkupMoreInfoBox',
    alias: 'widget.alertmessage',

    requires: [
        'Ext.fx.Animator',
        'Ext.util.DelayedTask'
    ],
    
    tpl: [
        '<div class="alert alert-{type}{extracls}{closablecls}" style="{style}">',
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
     * @cfg {String} [extracls=undefined]
     * Extra css classes. Example: ``"flat compact"``.
     */

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
     * @cfg {string|array} [messagetpl]
     * An XTemplate string or array to use instead of ``message``.
     * Requires that you specify ``messagedata``.
     */
    messagetpl: null,

    /**
     * @cfg {Object} [messagedata]
     * Data for ``messagetpl``.
     */
    messagedata: undefined,


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

    moretext: gettext('Details'),
    lesstext: gettext('Details'),

    initComponent: function() {
        var cls = 'bootstrap devilry_extjsextras_alertmessage';
        if(this.cls) {
            cls = Ext.String.format('{0} {1}', cls, this.cls);
        }
        this.cls = cls;
        this.callParent(arguments);
        this.update(this.messagetpl || this.message, this.type, this.messagedata);

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
            this.cancelTask = new Ext.util.DelayedTask(function(){
                this.fadeOutAndClose();
            }, this);
            this.addListener({
                scope: this,
                element: 'el',
                delegate: 'div.alert',
                //mouseover: this._onMouseOver,
                mouseleave: this._onMouseLeave,
                mouseenter: this._onMouseEnter
            });
            this._deferAutoclose();
        }
    },

    _deferAutoclose: function() {
        this.cancelTask.delay(1000*this.autoclose);
    },

    _onMouseEnter: function() {
        this.cancelTask.cancel(); // We do not close the message while mouse is over it.
    },
    _onMouseLeave: function() {
        this._deferAutoclose();
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
                    opacity: 1
                },
                100: {
                    opacity: 0.1
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
     *
     * @param messageOrTpl Message string, or XTemplate array/string if ``data`` is specified.
     * @param type The message type. Defaults to ``this.type`` if ``undefined``.
     * @param data If this is specified, ``message`` is an XTemplate config
     *    (see the ``messagetpl`` config), and ``data`` is the data for the
     *    template.
     * */
    update: function(messageOrTpl, type, data) {
        if(type) {
            this.type = type;
        }
        if(data) {
            this.setTplAttrs(data);
            this.message = Ext.create('Ext.XTemplate', messageOrTpl).apply(data);
        } else {
            this.message = messageOrTpl;
        }
        var style = '';
        if(!Ext.isEmpty(this.boxMargin)) {
            style = Ext.String.format('margin: {0};', this.boxMargin);
        }
        this.callParent([{
            type: this.type,
            message: this.message,
            title: this.title,
            style: style,
            closable: this.closable,
            extracls: Ext.isEmpty(this.extracls)? '': ' ' + this.extracls,
            closablecls: this.closable? ' closable': ''
        }]);
    },

    updateData: function(data, type) {
        this.update(this.messagetpl, type, data);
    }
});
