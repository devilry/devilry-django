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
        this.route.add("", 'dashboard');
        this.route.add("/@@dashboard/shortcutlist", 'shortcutlist');
        this.route.add("/:subject/:period", 'period_show');
        this.route.add("/:subject/:period/@@edit", 'period_edit');
        this.route.add("/:subject/:period/:assignment", 'assignment_show');
        this.route.start();
    },

    dashboard: function() {
        this.setView({xtype: 'component', html: 'dashboard'});
    },

    shortcutlist: function() {
        this.setView({xtype: 'shortcutlist'});
    },

    period_show: function(action, subject, period) {
        console.log('PE', action, subject, period);
    },
    period_edit: function(action, subject, period) {
        console.log(action, subject, period);
    },

    assignment_show: function(action, subject, period, assignment) {
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
