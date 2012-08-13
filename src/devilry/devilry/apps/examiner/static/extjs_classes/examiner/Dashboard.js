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
            flex: 1,
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
            model: Ext.ModelManager.getModel('devilry.apps.examiner.simplified.SimplifiedStaticFeedback'),
            dashboard_url: this.dashboardUrl,
            flex: 1,
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
                //margin: '10 0 0 0',
                border: false,
                flex: 1,
                autoScroll: true,
                layout: {
                    type: 'vbox',
                    align: 'stretch'
                },
                items: [activeAssignmentsView, {
                    xtype: 'container',
                    margin: '10 0 0 0',
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
