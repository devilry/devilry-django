Ext.define('devilry.examiner.Dashboard', {
    extend: 'Ext.container.Container',
    alias: 'widget.examiner-dashboard',

    requires: [
        'devilry.examiner.ActiveAssignmentsView',
        'devilry.examiner.RecentDeliveriesView',
        'devilry.examiner.RecentFeedbacksView'
    ],

    /**
     * @cfg {string} [dashboardUrl]
     */
    dasboardUrl: undefined,

    initComponent: function() {
        Ext.apply(this, {
            layout: 'anchor',
            autoScroll: true,
            defaults: {
                anchor: '100%'
            },
            items: [{
                xtype: 'examiner_activeassignmentsview',
                model: Ext.ModelManager.getModel('devilry.apps.examiner.simplified.SimplifiedAssignment'),
                dashboard_url: this.dashboardUrl
            }, {
                xtype: 'container',
                margin: '10 0 0 0',
                layout: 'column',
                items: [{
                    xtype: 'examiner_recentdeliveriesview',
                    model: Ext.ModelManager.getModel('devilry.apps.examiner.simplified.SimplifiedDelivery'),
                    dashboard_url: this.dashboardUrl,
                    columnWidth: 0.5,
                    margin: '0 10px 0 0',
                    urlCreateFn: function(record) {
                        return Ext.String.format(
                            "{0}assignmentgroup/{1}?deliveryid={2}",
                            this.dashboardUrl,
                            record.get('deadline__assignment_group'),
                            record.get('id')
                        );
                    },
                    urlCreateFnScope: this
                }, {
                    xtype: 'examiner_recentfeedbackview',
                    model: Ext.ModelManager.getModel('devilry.apps.examiner.simplified.SimplifiedStaticFeedback'),
                    dashboard_url: this.dashboardUrl,
                    columnWidth: 0.5,
                    margin: '0 0 0 10px',
                    urlCreateFn: function(record) {
                        return Ext.String.format(
                            "{0}assignmentgroup/{1}?deliveryid={2}",
                            this.dashboardUrl,
                            record.get('delivery__deadline__assignment_group'),
                            record.get('delivery')
                        );
                    },
                    urlCreateFnScope: this
                }]
            }]
        });
        this.callParent(arguments);
    }
});
