Ext.define('devilry.student.Dashboard', {
    extend: 'Ext.container.Container',
    alias: 'widget.student-dashboard',

    requires: [
        'devilry.student.StudentSearchWidget',
        'devilry.student.AddDeliveriesGrid',
        'devilry.student.browseperiods.BrowsePeriods',
        'devilry_extjsextras.Router'
    ],

    /**
     * @cfg {string} [dashboardUrl]
     */
    
    //constructor: function(config) {
        //this.initConfig(config);
        //this.callParent([config]);
    //},
    
    initComponent: function() {
        var assignmentgroup_store = Ext.create('Ext.data.Store', {
            model: Ext.ModelManager.getModel('devilry.apps.student.simplified.SimplifiedAssignmentGroup'),
            remoteFilter: true,
            remoteSort: true,
            autoSync: true
        });
        var recentDeliveries = Ext.create('devilry.examiner.RecentDeliveriesView', {
            model: Ext.ModelManager.getModel('devilry.apps.student.simplified.SimplifiedDelivery'),
            showStudentsCol: false,
            columnWidth: 0.5,
            urlCreateFn: function(record) {
                return Ext.String.format(
                    "{0}assignmentgroup/{1}?deliveryid={2}",
                    this.dashboardUrl,
                    record.get('deadline__assignment_group'),
                    record.get('id')
                );
            },
            urlCreateFnScope: this
        });
        var recentFeedbacks = Ext.create('devilry.examiner.RecentFeedbacksView', {
            model: Ext.ModelManager.getModel('devilry.apps.student.simplified.SimplifiedStaticFeedback'),
            showStudentsCol: false,
            columnWidth: 0.5,
            urlCreateFn: function(record) {
                return Ext.String.format(
                    "{0}assignmentgroup/{1}?deliveryid={2}",
                    this.dashboardUrl,
                    record.get('delivery__deadline__assignment_group'),
                    record.get('delivery')
                );
            },
            urlCreateFnScope: this
        });

        Ext.apply(this, {
            layout: {
                type: 'vbox',
                align: 'stretch'
            },
            items: [{
                xtype: 'panel',
                flex: 1,
                layout: 'fit',
                border: false,
                items: [{
                    xtype: 'tabpanel',
                    border: false,
                    items: [{
                        xtype: 'panel',
                        title: gettext('Dashboard'),
                        itemId: 'dashboard',
                        bodyPadding: 10,
                        autoScroll: true,
                        items: [{
                            xtype: 'studentsearchwidget',
                            urlPrefix: this.dashboardUrl
                        }, {
                            xtype: 'student-add-deliveriesgrid',
                            store: assignmentgroup_store,
                            urlCreateFn: function(record) {
                                return this.dashboardUrl + "add-delivery/" + record.get('id');
                            },
                            urlCreateFnScope: this
                        }, {
                            xtype: 'container',
                            margin: '20 0 0 0',
                            layout: 'column',
                            items: [recentDeliveries, recentFeedbacks]
                        }]
                    }, {
                        xtype: 'student-browseperiods',
                        title: gettext('Browse all')
                    }]
                }]
            }]
        });
        this.on('render', this._onRender, this);
        this.callParent(arguments);
    },

    _onRender: function() {
        //this.route = Ext.create('devilry_extjsextras.Router', this);
        //this.route.add("", 'dashboard');
        //this.route.add("/browse/", 'browse');
        //this.route.start();
    },

    dashboard: function() {
        //console.log('dashboard');
        //this.down('#dashboard').show();
    },

    browse: function() {
        //console.log('browse');
        //this.down('student-browseperiods').show();
    }
});
