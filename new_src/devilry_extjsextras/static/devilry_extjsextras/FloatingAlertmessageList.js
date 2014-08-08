/**
*  AlertMessageList that floats and automatically closes when all messages are closed.
*/ 
Ext.define('devilry_extjsextras.FloatingAlertmessageList', {
    extend: 'devilry_extjsextras.AlertMessageList',
    alias: 'widget.floatingalertmessagelist',
    cls: 'devilry_extjsextras_floatingalertmessagelist',

    messageDefaults: {
        closable: true,
        boxMargin: '0'
    },

    //onClose: function(alertmessage) {
        //this.callParent(arguments);
    //},

    initComponent: function() {
        Ext.apply(this, {
            hidden: true,
            border: false,
            frame: false,
            floating: true,
            shadow: false,
            bodyPadding: 0,
            sidePadding: 10
        });
        this._setupAutosizing();
        this.callParent(arguments);
    },

    _setupAutosizing: function() {
        Ext.fly(window).on('resize', this._onWindowResize, this);
        this.on('show', this._onShowWindow, this);
    },
    _onShowWindow: function() {
        this._setSizeAndPosition();
        // NOTE: Defer to work around the problem of the window triggering show-event before the
        // message is rendered completely. Without this, setSize will get the wrong height
        Ext.defer(function () {
            this._setSizeAndPosition();
        }, 100, this);
        Ext.defer(function () {
            this._setSizeAndPosition();
        }, 400, this);
    },
    _onWindowResize: function() {
        if(this.isVisible() && this.isFloating()) {
            this._setSizeAndPosition();
        }
    },
    _setSizeAndPosition: function() {
        if(this.isFloating()) {
            var bodysize = Ext.getBody().getViewSize();
            var width = bodysize.width * 0.42;
            var left = bodysize.width - width - this.sidePadding;
            this.setSize({
                width: width
            });
            this.setPosition(left, 0);
        }
    }
});
