/** Base class for windows used to Edit/Create RestfulSimplified models. */
Ext.define('devilry.extjshelpers.RestfulSimplifiedEditWindowBase', {
    extend: 'devilry.extjshelpers.MaximizableWindow',
    //width: 800,
    //height: 600,
    layout: 'fit',
    maximizable: true,
    modal: true,

    /**
     * @cfg
     * The {@link devilry.extjshelpers.RestfulSimplifiedEditPanel} to use for editing.
     */
    editpanel: undefined,
    
    initComponent: function() {
        var me = this;

        var form = this.editpanel.down('form');
        if(!this.width && form.suggested_windowsize) {
            this.width = form.suggested_windowsize.width,
            this.height = form.suggested_windowsize.height
        }
        this._preferredWidth = this.width || 700;
        this._preferredHeight = this.height || 500;

        this.editpanel.addListener('saveSucess', function(record) {
            me.onSaveSuccess(record);
        });

        Ext.apply(this, {
            items: this.editpanel
        });
        this._setupAutosizing();
        this.callParent(arguments);
    },

    onSaveSuccess: function(record) {
        throw "Must implement onSaveSuccess()"
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
            var padding = 20;
            var bodysize = Ext.getBody().getViewSize();
            var bodyWidth = bodysize.width - padding;
            var bodyHeight = bodysize.height - padding;
            var height = bodyHeight < this._preferredHeight? bodyHeight: this._preferredHeight;
            var width = bodyWidth < this._preferredWidth? bodyWidth: this._preferredWidth;
            this.setSize({
                width: width,
                height: height,
            });
            this.center();
        }
    }
});
