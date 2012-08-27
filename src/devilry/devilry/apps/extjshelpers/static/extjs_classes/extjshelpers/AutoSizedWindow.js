Ext.define('devilry.extjshelpers.AutoSizedWindow', {
    extend: 'Ext.window.Window',
    maximizable: false,
    windowPadding: 20,

    initComponent: function() {
        this._preferredWidth = this.width;
        this._preferredHeight = this.height;
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
            var padding = this.windowPadding;
            var bodysize = Ext.getBody().getViewSize();
            var bodyWidth = bodysize.width - padding;
            var bodyHeight = bodysize.height - padding;
            if(this._preferredHeight) {
                var height = bodyHeight < this._preferredHeight? bodyHeight: this._preferredHeight;
            }
            if(this._preferredWidth) {
                var width = bodyWidth < this._preferredWidth? bodyWidth: this._preferredWidth;
            }
            this.setSize({
                width: width,
                height: height,
            });
            this.center();
        }
    }
});
