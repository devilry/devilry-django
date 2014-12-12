/** A button-like component with ``click``-event, a special pressed css class,
 * and the ability to add an "extra" css class. */
Ext.define('devilry_header.FlatButton', {
    extend: 'Ext.Component',
    alias: 'widget.devilryheader_flatbutton',
    loadingCls: 'flatbutton_loading',
    cls: 'flatbutton',
    overCls: 'flatbutton_hover',
    pressedCls: 'flatbutton_pressed',
    notPressedCls: 'flatbutton_not_pressed',
    enableToggle: false,

    tpl: [
        '<div class="textwrapper">{text}</div>'
    ],

    data: {
        text: gettext('Loading') + ' ...'
    },

    constructor: function(config) {
        var loadingCls = config.loadingCls || this.loadingCls;
        var notPressedCls = config.notPressedCls || this.notPressedCls;
        var cls = config.cls || this.cls;
        cls = Ext.String.format('{0} {1} {2}', cls, loadingCls, notPressedCls);
        if(config.enableToggle) {
            cls += ' flatbutton_toggleable';
        }
        config.cls = cls;
        this.currentCls = loadingCls;

        this.addEvents(
            'click'
        );
        if(config.enableToggle) {
            this.pressed = false;
        }
        this.callParent([config]);
    },

    initComponent: function() {
        this.on({
            scope: this,
            render: this._onRender
        });
        this.callParent(arguments);
    },

    _changeCls: function(cls) {
        this.removeCls(this.currentCls);
        this.addCls(cls);
        this.currentCls = cls;
    },

    /** Set the extra class. Replaces ``flatbutton_loading`` first time it is called. */
    addExtraClass: function(cls) {
        this._changeCls(cls);
    },

    /** Set button text */
    setText: function(text) {
        this.update({
            text: text
        });
    },

    /** Add the ``pressedCls`` to css classes. */
    setPressedCls: function() {
        this.removeCls(this.notPressedCls);
        this.addCls(this.pressedCls);
    },

    /** Remove the ``pressedCls`` from css classes. */
    setNotPressedCls: function() {
        this.removeCls(this.pressedCls);
        this.addCls(this.notPressedCls);
    },

    _onRender: function() {
        this.mon(this.getEl(), {
            scope: this,
            click: this._onClick
        });
    },

    toggle: function() {
        if(this.enableToggle) {
            this._onClick();
        } else {
            throw "Can not toggle unless enableToggle==true";
        }
    },

    _onClick: function() {
        if(this.enableToggle) {
            this.pressed = !this.pressed;
            this.fireEvent('toggle', this, this.pressed);
        } else {
            this.fireEvent('click', this);
        }
    },

    setPressed:function (pressed) {
        this.pressed = pressed;
        if(pressed) {
            this.setPressedCls();
        } else {
            this.setNotPressedCls();
        }
    },

    setPressedWithEvent:function (pressed) {
        if(pressed !== this.pressed) {
            this.setPressed(pressed);
            this.fireEvent('toggle', this, this.pressed);
        }
    }
});
