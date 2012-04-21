Ext.define('devilry.student.Dashboard', {
    extend: 'Ext.container.Container',
    alias: 'widget.student-dashboard',

    requires: [
        'devilry.student.StudentSearchWidget',
        'devilry.student.AddDeliveriesGrid',
        'devilry.student.browseperiods.BrowsePeriods'
    ],

    /**
     * @cfg
     */
    dasboardUrl: undefined,
    
    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },
    
    initComponent: function() {
        var assignmentgroup_store = Ext.create('Ext.data.Store', {
            model: Ext.ModelManager.getModel('devilry.apps.student.simplified.SimplifiedAssignmentGroup'),
            remoteFilter: true,
            remoteSort: true,
            autoSync: true
        });
        var addDeliveriesGrid = Ext.create('devilry.student.AddDeliveriesGrid', {
            store: assignmentgroup_store,
            dashboard_url: this.dashboardUrl,
            minHeight: 140,
            flex: 1
        });

        var recentDeliveries = Ext.create('devilry.examiner.RecentDeliveriesView', {
            model: Ext.ModelManager.getModel('devilry.apps.student.simplified.SimplifiedDelivery'),
            showStudentsCol: false,
            dashboard_url: this.dashboardUrl,
            flex: 1
        });
        var recentFeedbacks = Ext.create('devilry.examiner.RecentFeedbacksView', {
            model: Ext.ModelManager.getModel('devilry.apps.student.simplified.SimplifiedStaticFeedback'),
            showStudentsCol: false,
            dashboard_url: this.dashboardUrl,
            flex: 1
        });

        var searchwidget = Ext.create('devilry.student.StudentSearchWidget', {
            urlPrefix: DASHBOARD_URL,
            hidden: false
        });


        Ext.apply(this, {
            layout: {
                type: 'vbox',
                align: 'stretch'
            },
            items: [
                searchwidget,
                {xtype:'box', height: 20},
            {
                xtype: 'panel',
                flex: 1,
                layout: 'fit',
                border: false,
                items: [{
                    xtype: 'tabpanel',
                    border: false,
                    items: [{
                        xtype: 'panel',
                        title: 'Dashboard',
                        bodyPadding: 10,
                        autoScroll: true,
                        layout: {
                            type: 'vbox',
                            align: 'stretch'
                        },
                        items: [addDeliveriesGrid, {
                            xtype: 'container',
                            margin: {top: 10},
                            layout: {
                                type: 'hbox',
                                align: 'stretch'
                            },
                            height: 200,
                            width: 800, // Needed to avoid layout issue in FF3.6
                            items: [recentDeliveries, {xtype: 'box', width: 40}, recentFeedbacks]
                        }]
                    }, {
                        xtype: 'student-browseperiods',
                        title: 'Browse all'
                    }]
                }]
            }]
        });
        this.callParent(arguments);
    }
});
