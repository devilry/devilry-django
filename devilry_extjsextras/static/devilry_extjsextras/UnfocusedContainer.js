Ext.define('devilry_extjsextras.UnfocusedContainer', {
    extend: 'Ext.container.Container',
    alias: 'widget.unfocusedcontainer',
    cls: 'devilry_extjsextras_unfocusedcontainer',

    defaultOpacity: 0.6,
    hoverOpacity: 1.0,

    initComponent: function() {
        this.on('render', this._onRender, this);
        this.callParent(arguments);
    },
    _onRender: function() {
        this.getEl().setOpacity(this.defaultOpacity);
        this.getEl().on({
            scope: this,
            mouseenter: this._onMouseEnter,
            mouseleave: this._onMouseLeave
        });
    },
    _onMouseEnter: function() {
        this.getEl().setOpacity(this.hoverOpacity);
        this.mouseEnterExtras();
    },
    _onMouseLeave: function() {
        this.getEl().setOpacity(this.defaultOpacity);
        this.mouseLeaveExtras();
    },

    mouseEnterExtras: function() {
        
    },
    mouseLeaveExtras: function() {

    }
});
