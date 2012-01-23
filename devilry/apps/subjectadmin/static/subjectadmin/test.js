Ext.application({
    name: 'subjectadmin',
    appFolder: DevilrySettings.DEVILRY_STATIC_URL + '/subjectadmin/app',

    controllers: [
        'ShortcutsTestMock',
    ],

    launch: function() {
        this.viewport = Ext.create('Ext.container.Viewport', {
            layout: 'fit'
        });
        this.route = Ext.create('guibase.Router', this);
        this.route.add("", 'shortcutlist');
        this.route.add(/^\/shortcutlist$/, 'shortcutlist');
        this.route.add(/^\/period\/(\d+)$/, 'period');
        this.route.add(/^\/assignment\/(\d+)$/, 'assignment');
        this.route.add("/browse/:subject/:period/:assignment", 'assignment');
        this.route.start();
    },

    shortcutlist: function() {
        this.setView({xtype: 'shortcutlist'});
    },

    period: function(action, id) {
        console.log('PE', action, id);
    },

    assignment: function(action, subject, period, assignment) {
        console.log('Assignment', subject, period, assignment);
    },

    routeNotFound: function() {
        this.setView({
            xtype: 'component',
            html: '<h1>Not found</h1><p>Route not found.</p>'
        });
    },

    setView: function(component) {
        this.viewport.removeAll();
        this.viewport.add(component);
    }
});
