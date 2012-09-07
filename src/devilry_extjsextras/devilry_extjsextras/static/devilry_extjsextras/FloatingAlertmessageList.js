/**
*  AlertMessageList that floats and automatically closes when all messages are closed.
*/ 
Ext.define('devilry_extjsextras.FloatingAlertMessageList', {
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
    },
    _onWindowResize: function() {
        if(this.isVisible() && this.isFloating()) {
            this._setSizeAndPosition();
        }
    },
    _setSizeAndPosition: function() {
        if(this.isFloating()) {
            var bodysize = Ext.getBody().getViewSize();
            var width = bodysize.width - this.sidePadding*2;
            this.setSize({
                width: width
            });
            this.setPosition(this.sidePadding, 0);
        }
    }
});
