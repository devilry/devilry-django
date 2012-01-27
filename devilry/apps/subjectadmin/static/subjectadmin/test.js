Ext.application({
    name: 'subjectadmin',
    appFolder: DevilrySettings.DEVILRY_STATIC_URL + '/subjectadmin/app',

    requires: [
        'guibase.RouteNotFound'
    ],

    controllers: [
        'ShortcutsTestMock',
        'Dashboard',
        'CreateNewAssignment',
        'ChoosePeriodTestMock'
    ],

    launch: function() {
        this.viewport = Ext.create('Ext.container.Viewport', {
            layout: 'fit'
        });
        this.route = Ext.create('guibase.Router', this);
        this.route.add("", 'dashboard');
        this.route.add("/@@create-new-assignment/@@chooseperiod", 'create_new_assignment_chooseperiod');
        this.route.add("/@@create-new-assignment/:period", 'create_new_assignment');
        //this.route.add("/:subject/:period", 'period_show');
        //this.route.add("/:subject/:period/@@edit", 'period_edit');
        //this.route.add("/:subject/:period/:assignment", 'assignment_show');

        // These views are only for unit tests
        this.route.add("/@@dashboard/shortcutlist", 'shortcutlist');
        this.route.add("/@@dashboard/actionlist", 'actionlist');
        this.route.start();
    },

    routeNotFound: function(route) {
        this.setView({
            xtype: 'routenotfound',
            data: {
                route: route.token
            }
        });
    },

    setView: function(component) {
        this.viewport.removeAll();
        this.viewport.add(component);
    },


    /*********************************************
     * Moch the actual interface
     ********************************************/
    dashboard: function() {
        this.setView({
            xtype: 'dashboard'
        });
    },

    create_new_assignment: function() {
        this.setView({
            xtype: 'createnewassignmentform'
        });
    },

    create_new_assignment_chooseperiod: function() {
        this.setView({
            xtype: 'chooseperiod',
            nexturlformat: '/@@create-new-assignment/{0}'
        });
    },

    //period_show: function(route, subject, period) {
        //console.log('PE', route, subject, period);
    //},
    //period_edit: function(route, subject, period) {
        //console.log(route, subject, period);
    //},

    //assignment_show: function(route, subject, period, assignment) {
        //console.log('Assignment', subject, period, assignment);
    //},

    /*********************************************
     * Only for testing.
     ********************************************/
    shortcutlist: function() {
        this.setView({xtype: 'shortcutlist'});
    },

    actionlist: function() {
        this.setView({
            xtype: 'actionlist',
            data: {
                title: 'Action list test',
                links: [{
                    url: '#/@@actionitem-1',
                    text: 'Action item 1'
                }, {
                    url: '#/@@actionitem-2',
                    text: 'Action item 2'
                }]
            }
        });
    },
});
