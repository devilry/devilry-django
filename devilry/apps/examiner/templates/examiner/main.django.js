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

    function createActiveAssignmentsView() {
        var activeAssignmentsView = Ext.create('devilry.examiner.ActiveAssignmentsView', {
            model: Ext.ModelManager.getModel('devilry.apps.examiner.simplified.SimplifiedAssignment'),
            dashboard_url: DASHBOARD_URL,
            minHeight: 140,
            flex: 1
        });
        var recentDeliveries = Ext.create('devilry.examiner.RecentDeliveriesView', {
            model: Ext.ModelManager.getModel('devilry.apps.examiner.simplified.SimplifiedDelivery'),
            dashboard_url: DASHBOARD_URL,
            flex: 1
        });
        var recentFeedbacks = Ext.create('devilry.examiner.RecentFeedbacksView', {
            model: Ext.ModelManager.getModel('devilry.apps.examiner.simplified.SimplifiedStaticFeedback'),
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



{% endblock %}


{% block onready %}
    {{ block.super }}
    Ext.getBody().unmask();

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
            items: [searchwidget, {xtype:'box', height: 20}, {
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
    searchwidget.show();
    createActiveAssignmentsView();
{% endblock %}
