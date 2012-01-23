Ext.application({
    name: 'subjectadmin',
    appFolder: DevilrySettings.DEVILRY_STATIC_URL + '/subjectadmin/app',

    controllers: [
        'ShortcutsTestMock',
    ],

    launch: function() {
        this.route = Ext.create('guibase.Router', this);
        this.route.add("^$", 'index');
        this.route.add(/^\/shortcutlist$/, 'shortcutlist');
        this.route.add(/^\/period\/(\d+)$/, 'period');
        this.route.add(/^\/assignment\/(\d+)$/, 'assignment');
        this.route.start();

        Ext.create('Ext.container.Viewport', {
            layout: 'fit',
            items: {
                xtype: 'shortcutlist'
            }
        });
    },

    index: function() {
        console.log('index');
    },

    shortcutlist: function(action) {
        console.log(action);
    },

    period: function(action, id) {
        console.log('PE', action, id);
    },

    assignment: function(action, id) {
        console.log('Assignment!', id);
    },

    routeNotFound: function() {
        alert('ROUTE NOT FOUND');
    }
});
