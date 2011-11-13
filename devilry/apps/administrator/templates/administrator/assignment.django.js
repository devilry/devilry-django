{% extends "administrator/base.django.js" %}
{% load extjs %}

{% block imports %}
    {{ block.super }}
    Ext.require([
        //'devilry.administrator.assignment.Layout'
        'devilry.administrator.assignment.PrettyView',
        'devilry.extjshelpers.RestfulSimplifiedEditPanel',
        'devilry.extjshelpers.forms.administrator.Assignment'
    ]);
{% endblock %}


{% block appjs %}
    {{ block.super }}
    {{ restfulapi.RestfulSimplifiedDelivery|extjs_model }}
    {{ restfulapi.RestfulSimplifiedDeadline|extjs_model }}
    {{ restfulapi.RestfulSimplifiedRelatedStudent|extjs_model }}
    {{ restfulapi.RestfulSimplifiedRelatedExaminer|extjs_model }}
    {{ restfulapi.RestfulSimplifiedPeriod|extjs_model:"subject" }}
    {{ restfulapi.RestfulSimplifiedAssignment|extjs_model:"period,subject,admins" }};
    {{ restfulapi.RestfulSimplifiedAssignmentGroup|extjs_model:"feedback,feedbackdelivery,assignment,period,subject,users,tags,students_full_name" }};
    {{ gradeeditors.RestfulSimplifiedConfig|extjs_model }};
    var assignmentgroupstore = {{ restfulapi.RestfulSimplifiedAssignmentGroup|extjs_store }};
    {{ gradeeditors.RestfulSimplifiedFeedbackDraft|extjs_model }};

    {{ restfulapi.RestfulSimplifiedAssignmentGroup|extjs_model:"assignment,users,tags;Import" }};
{% endblock %}

{% block onready %}
    {{ block.super }}
    Ext.getBody().unmask();

    var prettyview = Ext.create('devilry.administrator.assignment.PrettyView', {
        //renderTo: 'content-main',
        modelname: {{ restfulapi.RestfulSimplifiedAssignment|extjs_modelname }},
        objectid: {{ objectid }},
        dashboardUrl: DASHBOARD_URL,
        assignmentgroupstore: assignmentgroupstore
        //assignmentgroupPrevApprovedStore: assignmentgroupPrevApprovedStore
    });

    var heading = Ext.ComponentManager.create({
        xtype: 'component',
        //renderTo: 'content-heading',
        data: {},
        tpl: [
            '<tpl if="long_name">',
            '   <h1>{parentnode__parentnode__long_name}</h1>',
            '   <h2>{parentnode__long_name}</h2>',
            '   <h3>{long_name} ({short_name})</h3>',
            '</tpl>'
        ]
    });

    prettyview.addListener('loadmodel', function(record) {
        heading.update(record.data);
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
            //region: 'center',
            //xtype: 'administrator-periodlayout',
            //periodid: {{ objectid }},
            //padding: {left: 20, right: 20}
            xtype: 'panel',
            region: 'center',
            items: [heading, prettyview]
        }]
    });
{% endblock %}
