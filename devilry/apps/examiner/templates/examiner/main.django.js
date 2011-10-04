{% extends "examiner/base.django.js" %}
{% load extjs %}

{% block imports %}
    {{ block.super }}
    Ext.require([
        'devilry.extjshelpers.PermissionChecker',
        'devilry.examiner.ActiveAssignmentsView',
        'devilry.examiner.RecentDeliveriesView',
        'devilry.examiner.RecentFeedbacksView'
    ]);
{% endblock %}

{% block appjs %}
    {{ block.super }}

    var dashboard_assignment_model = {{ restfulapi.RestfulSimplifiedAssignment|extjs_model:"subject,period" }}
    var dashboard_delivery_model = {{ restfulapi.RestfulSimplifiedDelivery|extjs_model:"subject,period,assignment,assignment_group,candidates" }}
    var dashboard_feedback_model = {{ restfulapi.RestfulSimplifiedStaticFeedback|extjs_model:"subject,period,assignment,assignment_group,candidates" }}
    function createActiveAssignmentsView() {
        var activeAssignmentsView = Ext.create('devilry.examiner.ActiveAssignmentsView', {
            model: dashboard_assignment_model,
            dashboard_url: DASHBOARD_URL,
            minHeight: 140,
            flex: 1
        });
        var recentDeliveries = Ext.create('devilry.examiner.RecentDeliveriesView', {
            model: dashboard_delivery_model,
            dashboard_url: DASHBOARD_URL,
            flex: 1
        });
        var recentFeedbacks = Ext.create('devilry.examiner.RecentFeedbacksView', {
            model: dashboard_feedback_model,
            dashboard_url: DASHBOARD_URL,
            flex: 1
        });
        
        Ext.getCmp('assignmentcontainer').add([activeAssignmentsView, {
            xtype: 'container',
            margin: {top: 10},
            layout: {
                type: 'hbox',
                align: 'stretch'
            },
            height: 200,
            items: [recentDeliveries, {xtype: 'box', width: 40}, recentFeedbacks]
        }]);
    }


    {{ restfulapi.RestfulSimplifiedAssignmentGroup|extjs_model:";PermissionCheck" }};
    var assignmentgroup_permcheckstore = {{ restfulapi.RestfulSimplifiedAssignmentGroup|extjs_store:"PermissionCheck" }};
    assignmentgroup_permcheckstore.pageSize = 1;

{% endblock %}


{% block onready %}
    {{ block.super }}


    function createPermissionChecker() {
    }

    var permchecker = Ext.create('devilry.extjshelpers.PermissionChecker', {
        stores: [assignmentgroup_permcheckstore],
        emptyHtml: '<div class="section info-small extravisible-small"><h1>{{ DEVILRY_EXAMINER_NO_PERMISSION_MSG.title }}</h1>' +
            '<p>{{ DEVILRY_EXAMINER_NO_PERMISSION_MSG.body }}</p></div>',
        listeners: {
            allLoaded: function() {
                Ext.getBody().unmask();
            },
            hasPermission: function() {
                //Ext.getDom('has-permission-section').style.display = 'block';
                //Ext.getDom('searchsection').style.display = 'block';
                //createActiveAssignmentsView();
                searchwidget.show();
                createActiveAssignmentsView();
            }
        }
    });
    assignmentgroup_permcheckstore.load();

    Ext.create('Ext.container.Viewport', {
        layout: 'border',
        style: 'background-color: transparent',
        items: [{
            region: 'north',
            xtype: 'pageheader',
            navclass: 'examiner'
        }, {
            region: 'south',
            xtype: 'pagefooter'
        }, {
            region: 'center',
            xtype: 'container',
            border: false,
            padding: {left: 20, right: 20},
            layout: {
                type: 'vbox',
                align: 'stretch'
            },
            items: [searchwidget, permchecker, {xtype:'box', height: 20}, {
                xtype: 'panel',
                flex: 1,
                autoScroll: true,
                layout: {
                    type: 'vbox',
                    align: 'stretch'
                },
                border: false,
                id: 'assignmentcontainer'
            }]
        }]
    });
{% endblock %}
