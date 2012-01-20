{% extends "student/base.django.js" %}
{% load extjs %}

{% block imports %}
    {{ block.super }}
    Ext.require('devilry.student.StudentSearchWidget');
    Ext.require('devilry.extjshelpers.PermissionChecker');
    Ext.require('devilry.student.AddDeliveriesGrid');
    Ext.require('devilry.student.browseperiods.BrowsePeriods');
{% endblock %}

{% block appjs %}
    {{ block.super }}

    var ag_model = {{ restfulapi.RestfulSimplifiedAssignmentGroup|extjs_model:"subject,period,assignment,users,feedback,feedbackdelivery" }};

    function createGrids() {
        var ag_store = Ext.create('Ext.data.Store', {
            model: Ext.ModelManager.getModel('devilry.apps.student.simplified.SimplifiedAssignmentGroup'),
            remoteFilter: true,
            remoteSort: true,
            autoSync: true
        });
        var addDeliveriesGrid = Ext.create('devilry.student.AddDeliveriesGrid', {
            store: ag_store,
            dashboard_url: DASHBOARD_URL,
            minHeight: 140,
            flex: 1
        });

        var recentDeliveries = Ext.create('devilry.examiner.RecentDeliveriesView', {
            model: Ext.ModelManager.getModel('devilry.apps.student.simplified.SimplifiedDelivery'),
            showStudentsCol: false,
            dashboard_url: DASHBOARD_URL,
            flex: 1
        });
        var recentFeedbacks = Ext.create('devilry.examiner.RecentFeedbacksView', {
            model: Ext.ModelManager.getModel('devilry.apps.student.simplified.SimplifiedStaticFeedback'),
            showStudentsCol: false,
            dashboard_url: DASHBOARD_URL,
            flex: 1
        });
        Ext.getCmp('assignmentcontainer').add({
            xtype: 'tabpanel',
            bodyPadding: 10,
            items: [{
                xtype: 'panel',
                title: 'Dashboard',
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
        });
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
            navclass: 'student'
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
                layout: 'fit',
                border: false,
                id: 'assignmentcontainer'
            }]
        }]
    });
    searchwidget.show();
    createGrids();
{% endblock %}
