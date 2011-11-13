{% extends "administrator/base.django.js" %}
{% load extjs %}

{% block imports %}
    {{ block.super }}
    Ext.require([
        'devilry.administrator.assignment.Layout'
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
            xtype: 'administrator-assignmentlayout',
            assignmentgroupstore: assignmentgroupstore,
            assignmentid: {{ objectid }},
            padding: {left: 20, right: 20}
        }]
    });
{% endblock %}
