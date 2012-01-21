Ext.define('devilry.examiner.Dashboard', {
    extend: 'Ext.container.Container',
    alias: 'widget.examiner-dashboard',

    requires: [
        'devilry.examiner.ActiveAssignmentsView',
        'devilry.examiner.RecentDeliveriesView',
        'devilry.examiner.RecentFeedbacksView',
        'devilry.examiner.ExaminerSearchWidget'
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
        var activeAssignmentsView = Ext.create('devilry.examiner.ActiveAssignmentsView', {
            model: Ext.ModelManager.getModel('devilry.apps.examiner.simplified.SimplifiedAssignment'),
            dashboard_url: this.dashboardUrl,
            minHeight: 140,
            flex: 1
        });
        var recentDeliveries = Ext.create('devilry.examiner.RecentDeliveriesView', {
            model: Ext.ModelManager.getModel('devilry.apps.examiner.simplified.SimplifiedDelivery'),
            dashboard_url: this.dashboardUrl,
            flex: 1
        });
        var recentFeedbacks = Ext.create('devilry.examiner.RecentFeedbacksView', {
            model: Ext.ModelManager.getModel('devilry.apps.examiner.simplified.SimplifiedStaticFeedback'),
            dashboard_url: this.dashboardUrl,
            flex: 1
        });

        var searchwidget = Ext.create('devilry.examiner.ExaminerSearchWidget', {
            urlPrefix: this.dashboardUrl
        });


        Ext.apply(this, {
            layout: {
                type: 'vbox',
                align: 'stretch'
            },
            items: [searchwidget, {
                xtype: 'panel',
                margin: {top: 10},
                border: false,
                flex: 1,
                bodyPadding: 10,
                autoScroll: true,
                layout: {
                    type: 'vbox',
                    align: 'stretch'
                },
                items: [activeAssignmentsView, {
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
            }]
        });
        this.callParent(arguments);
    }
});
