{% extends "administrator/base.django.js" %}
{% load extjs %}

{% block imports %}
    {{ block.super }}
    Ext.require([
        'devilry.administrator.PeriodAdminLayout'
    ]);
{% endblock %}


{% block appjs %}
    {{ block.super }}
    {{ restfulapi.RestfulSimplifiedSubject|extjs_model }};
    {{ restfulapi.RestfulSimplifiedPeriod|extjs_model:"subject,admins" }};
    {{ restfulapi.RestfulSimplifiedRelatedStudent|extjs_model }};
    {{ restfulapi.RestfulSimplifiedRelatedStudentKeyValue|extjs_model }};
    {{ restfulapi.RestfulSimplifiedAssignment|extjs_model }};
    {{ restfulapi.RestfulSimplifiedAssignmentGroup|extjs_model:"feedback" }};
    {{ restfulapi.RestfulSimplifiedCandidate|extjs_model }};
    {{ restfulapi.RestfulSimplifiedPeriodApplicationKeyValue|extjs_model }};
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
            xtype: 'administrator-periodadminlayout',
            periodid: {{ objectid }},
            padding: {left: 20, right: 20}
        }]
    });
{% endblock %}
