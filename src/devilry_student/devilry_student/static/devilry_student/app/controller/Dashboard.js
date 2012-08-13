Ext.define('devilry_student.controller.Dashboard', {
    extend: 'Ext.app.Controller',

    requires: [
        'devilry.student.StudentSearchWidget',
        'devilry.student.AddDeliveriesGrid',
        'devilry.student.browseperiods.BrowsePeriods',
        'devilry.examiner.RecentFeedbacksView',
        'devilry.examiner.RecentDeliveriesView',
        'devilry.apps.student.simplified.SimplifiedAssignmentGroup',
        'devilry.apps.student.simplified.SimplifiedDelivery',
        'devilry.apps.student.simplified.SimplifiedStaticFeedback'
    ],

    views: [
        'dashboard.Overview'
    ],

    refs: [{
        ref: 'dashboard',
        selector: 'viewport dashboard'
    }],

    init: function() {
        this.control({
            'viewport dashboard': {
                render: this._onRenderDashboard
            },
        });
    },

    _onRenderDashboard: function() {
        this.getDashboard().add([{
            xtype: 'studentsearchwidget',
            urlPrefix: this.dashboard_url
        }, {
            xtype: 'student-add-deliveriesgrid',
            store: this._createActiveAssignmentsStore(),
            urlCreateFn: function(record) {
                return DevilrySettings.DEVILRY_URLPATH_PREFIX + '/student/add-delivery/' + record.get('id');
            },
            urlCreateFnScope: this,
            margin: '20 0 0 0'
        }, {
            xtype: 'box',
            margin: '6 0 0 0',
            tpl: '<p><a class="browseall_link" href="{url}">{text}</a></p>',
            data: {
                url: '#/browse/',
                text: gettext('Browse all assignments and deliveries, including feedback')
            }
        }, {
            xtype: 'container',
            margin: '20 0 0 0',
            layout: 'column',
            items: [Ext.create('devilry.examiner.RecentDeliveriesView', {
                model: Ext.ModelManager.getModel('devilry.apps.student.simplified.SimplifiedDelivery'),
                showStudentsCol: false,
                dashboard_url: this.application.dashboard_url,
                columnWidth: 0.5,
                margin: '0 20 0 0'
            }), Ext.create('devilry.examiner.RecentFeedbacksView', {
                model: Ext.ModelManager.getModel('devilry.apps.student.simplified.SimplifiedStaticFeedback'),
                showStudentsCol: false,
                dashboard_url: this.application.dashboard_url,
                columnWidth: 0.5,
                margin: '0 0 20 0'
            })]
        }])
    },

    _createActiveAssignmentsStore: function() {
        var store = Ext.create('Ext.data.Store', {
            model: Ext.ModelManager.getModel('devilry.apps.student.simplified.SimplifiedAssignmentGroup'),
            remoteFilter: true,
            remoteSort: true,
            autoSync: true
        });
        return store;
    }
});
