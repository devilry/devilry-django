Ext.define('devilry_extjsextras.AutoSizedWindow', {
    extend: 'Ext.window.Window',
    alias: 'widget.devilry_extjsextras_autosizedwindow',
    windowPadding: 20,

    initComponent: function() {
        this._preferredWidth = this.width;
        this._preferredHeight = this.height;
        this._setupAutosizing();
        this.maximizable = false;
        this.callParent(arguments);
    },

    _setupAutosizing: function() {
        Ext.fly(window).on('resize', this._onWindowResize, this);
        this.on('show', this._onShowWindow, this);
    },
    _onShowWindow: function() {
        this.setSizeAndPosition();
    },
    _onWindowResize: function() {
        if(this.isVisible() && this.isFloating()) {
            this.setSizeAndPosition();
        }
    },
    setSizeAndPosition: function() {
        if(this.isFloating()) {
            var padding = this.windowPadding;
            var bodysize = Ext.getBody().getViewSize();
            var bodyWidth = bodysize.width - padding;
            var bodyHeight = bodysize.height - padding;
            var height = bodyHeight;
            var width = bodyWidth;
            if(this._preferredHeight) {
                height = bodyHeight < this._preferredHeight? bodyHeight: this._preferredHeight;
            }
            if(this._preferredWidth) {
                width = bodyWidth < this._preferredWidth? bodyWidth: this._preferredWidth;
            }
            this.setSize({
                width: width,
                height: height
            });
            this.center();
        }
    },

    getPreferredHeight: function() {
        return this._preferredHeight;
    },
    getPreferredWidth: function() {
        return this._preferredWidth;
    }
});
