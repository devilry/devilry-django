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

    {{ restfulapi.RestfulSimplifiedNode|extjs_model }};
    {{ restfulapi.RestfulSimplifiedSubject|extjs_model }};
    {{ restfulapi.RestfulSimplifiedPeriod|extjs_model:"subject" }};
    {{ restfulapi.RestfulSimplifiedAssignment|extjs_model }};

    var nodestore = {{ restfulapi.RestfulSimplifiedNode|extjs_store }};
    var subjectstore = {{ restfulapi.RestfulSimplifiedSubject|extjs_store }};
    var periodstore = {{ restfulapi.RestfulSimplifiedPeriod|extjs_store }};
    nodestore.pageSize = 1;
    subjectstore.pageSize = 1;
    periodstore.pageSize = 1;
    var is_superuser = {{ user.is_superuser|lower }};
{% endblock %}

{% block onready %}
    {{ block.super }}


    var dashboard_assignment_model = {{ restfulapi.RestfulSimplifiedAssignment|extjs_model:"subject,period" }}
    var dashboard_periodmodel = {{ restfulapi.RestfulSimplifiedPeriod|extjs_model:"subject" }}
    var permchecker = Ext.create('devilry.extjshelpers.PermissionChecker', {
        stores: [nodestore, subjectstore, periodstore],
        //renderTo: 'no-permissions-message',
        emptyHtml: '<div class="section info-small extravisible-small"><h1>{{ DEVILRY_ADMINISTRATOR_NO_PERMISSION_MSG.title }}</h1>' +
            '<p>{{ DEVILRY_ADMINISTRATOR_NO_PERMISSION_MSG.body }}</p></div>',
        listeners: {
            allLoaded: function(loadedItems, loadedWithRecords) {
                Ext.getBody().unmask();
                if(is_superuser || loadedWithRecords > 0) {
                    var activeAssignmentsView = Ext.create('devilry.examiner.ActiveAssignmentsView', {
                        model: dashboard_assignment_model,
                        dashboard_url: DASHBOARD_URL
                    });
                    Ext.getCmp('active-assignments').add(activeAssignmentsView);

                    var activePeriodsView = Ext.create('devilry.extjshelpers.ActivePeriodsGrid', {
                        model: dashboard_periodmodel,
                        dashboard_url: DASHBOARD_URL
                    });
                    Ext.getCmp('active-periods').add(activePeriodsView);

                    searchwidget.show();
                }
            }
        }
    });

    var buttonbar = Ext.create('devilry.administrator.DashboardButtonBar', {
        node_modelname: {{ restfulapi.RestfulSimplifiedNode|extjs_modelname }},
        subject_modelname: {{ restfulapi.RestfulSimplifiedSubject|extjs_modelname }},
        period_modelname: {{ restfulapi.RestfulSimplifiedPeriod|extjs_modelname }},
        assignment_modelname: {{ restfulapi.RestfulSimplifiedAssignment|extjs_modelname }},
        is_superuser: is_superuser,
        nodestore: nodestore,
        subjectstore: subjectstore,
        periodstore: periodstore
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
            items: [searchwidget, {xtype:'box', height: 20}, permchecker, buttonbar, {
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

    nodestore.load();
    subjectstore.load();
    periodstore.load();
{% endblock %}
