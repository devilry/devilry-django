Ext.define('devilry_student.controller.BrowseHistory', {
    extend: 'Ext.app.Controller',

    requires: [
    ],

    views: [
        'browsehistory.Overview'
    ],

    refs: [{
        ref: 'overview',
        selector: 'viewport browsehistory'
    }],

    init: function() {
        this.control({
            'viewport browsehistory': {
                render: this._onRender
            },
        });
    },

    _onRender: function() {
    }
});
