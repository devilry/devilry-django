Ext.define('devilry_header.CurrentRoleButton', {
    extend: 'Ext.Component',
    alias: 'widget.devilryheader_currentrolebutton',
    cls: 'currentrolebutton currentrolebutton_loading',
    overCls: 'currentrolebutton_hover',
    //disabledCls: 'currentrolebutton_disabled',

    tpl: [
        '<div class="textwrapper">{text}</div>'
    ],

    data: {
        text: gettext('Loading ...')
    },

    constructor: function(config) {
        this.addEvents(
            'trigger'
        );
        this.callParent([config]);
    },

    initComponent: function() {
        this.currentCls = 'currentrolebutton_loading';
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

    setCurrentRole: function(text, cls) {
        this._changeCls(cls);
        this.update({
            text: text
        });
    },

    setPressedClass: function() {
        this.addCls('currentrolebutton_pressed');
    },
    removePressedClass: function() {
        this.removeCls('currentrolebutton_pressed');
    },

    _onRender: function() {
        this.mon(this.getEl(), {
            scope: this,
            click: this._onTrigger
        });
    },

    _onTrigger: function() {
        this.fireEvent('trigger', this);
    }
});
