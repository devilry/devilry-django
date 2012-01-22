Ext.define('subjectadmingui.controller.Actions', {
    extend: 'Ext.app.Controller',

    views: [
        'action.List'
    ],

    init: function() {
        this.control({
            'viewport > panel': {
                render: this.onPanelRendered
            }
        });
    },

    onPanelRendered: function() {
        console.log('The panel was rendered');
    }
});

