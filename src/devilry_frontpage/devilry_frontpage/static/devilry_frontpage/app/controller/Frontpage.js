Ext.define('devilry_frontpage.controller.Frontpage', {
    extend: 'Ext.app.Controller',

    requires: [
        'Ext.window.MessageBox'
    ],

    views: [
        'frontpage.Overview'
    ],

    refs: [{
        ref: 'overview',
        selector: 'viewport overview'
    }],

    init: function() {
        this.control({
            'viewport frontpage': {
                render: this._onRender
            }
        });
    },

    _onRender: function() {
    }
});
