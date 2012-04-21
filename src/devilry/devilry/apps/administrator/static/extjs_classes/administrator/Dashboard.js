Ext.define('devilry.administrator.Dashboard', {
    extend: 'Ext.container.Container',
    alias: 'widget.administrator-dashboard',

    requires: [
        'devilry.extjshelpers.PermissionChecker',
        'devilry.examiner.ActiveAssignmentsView',
        'devilry.administrator.DashboardButtonBar'
    ],

    /**
     * @cfg
     * 
     */
    dashboardUrl: undefined,
    
    initComponent: function() {
        var searchwidget = Ext.create('devilry.administrator.AdministratorSearchWidget', {
            urlPrefix: this.dashboardUrl
        });

        var buttonbar = Ext.create('devilry.administrator.DashboardButtonBar', {
            is_superuser: DevilryUser.is_superuser
        });

        var activeAssignmentsView = Ext.create('devilry.examiner.ActiveAssignmentsView', {
            model: Ext.ModelManager.getModel('devilry.apps.administrator.simplified.SimplifiedAssignment'),
            dashboard_url: this.dashboardUrl
        });

        var activePeriodsView = Ext.create('devilry.extjshelpers.ActivePeriodsGrid', {
            model: Ext.ModelManager.getModel('devilry.apps.administrator.simplified.SimplifiedPeriod'),
            dashboard_url: this.dashboardUrl
        });

        Ext.apply(this, {
            layout: {
                type: 'vbox',
                align: 'stretch'
            },
            items: [searchwidget, {xtype:'box', height: 20}, buttonbar, {
                xtype: 'container',
                flex: 1,
                layout: {
                    type: 'hbox',
                    align: 'stretch'
                },
                items: [{
                    xtype: 'panel',
                    flex: 3,
                    layout: 'fit',
                    border: false,
                    items: activePeriodsView
                }, {
                    xtype: 'box',
                    width: 30
                }, {
                    xtype: 'panel',
                    flex: 7,
                    layout: 'fit',
                    border: false,
                    items: activeAssignmentsView
                }]
            }]
        });
        this.callParent(arguments);
    }
});
