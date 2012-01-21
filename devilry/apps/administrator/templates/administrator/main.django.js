{% extends "administrator/base.django.js" %}
{% load extjs %}


{% block imports %}
    {{ block.super }}
    Ext.require('devilry.extjshelpers.PermissionChecker');
    Ext.require('devilry.examiner.ActiveAssignmentsView');
    Ext.require('devilry.administrator.DashboardButtonBar');
{% endblock %}


{% block appjs %}
    {{ block.super }}

    var is_superuser = {{ user.is_superuser|lower }};
{% endblock %}

{% block onready %}
    {{ block.super }}

    var buttonbar = Ext.create('devilry.administrator.DashboardButtonBar', {
        is_superuser: is_superuser
    });

    Ext.create('Ext.container.Viewport', {
        layout: 'border',
        style: 'background-color: transparent',
        items: [{
            region: 'north',
            xtype: 'pageheader',
            navclass: 'administrator'
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
                    id: 'active-periods'
                }, {
                    xtype: 'box',
                    width: 30
                }, {
                    xtype: 'panel',
                    flex: 7,
                    layout: 'fit',
                    border: false,
                    id: 'active-assignments'
                }]
            }]
        }]
    });
    Ext.getBody().unmask();
    var activeAssignmentsView = Ext.create('devilry.examiner.ActiveAssignmentsView', {
        model: Ext.ModelManager.getModel('devilry.apps.administrator.simplified.SimplifiedAssignment'),
        dashboard_url: DASHBOARD_URL
    });
    Ext.getCmp('active-assignments').add(activeAssignmentsView);

    var activePeriodsView = Ext.create('devilry.extjshelpers.ActivePeriodsGrid', {
        model: Ext.ModelManager.getModel('devilry.apps.administrator.simplified.SimplifiedPeriod'),
        dashboard_url: DASHBOARD_URL
    });
    Ext.getCmp('active-periods').add(activePeriodsView);

    searchwidget.show();
{% endblock %}
