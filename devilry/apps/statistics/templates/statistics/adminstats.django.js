{% extends "theme/common.django.html" %}
{% load extjs %}

{% block imports %}
    {{ block.super }}
    Ext.require('devilry.statistics.PeriodAdminLayout');
{% endblock %}

{% block appjs %}
    {{ RestfulSimplifiedPeriod|extjs_model:"subject" }};
    {{ RestfulSimplifiedRelatedStudent|extjs_model }}
    {{ RestfulSimplifiedRelatedStudentKeyValue|extjs_model }}
    {{ RestfulSimplifiedAssignment|extjs_model }};
    {{ RestfulSimplifiedAssignmentGroup|extjs_model:"feedback" }};
    {{ RestfulSimplifiedCandidate|extjs_model }};
    {{ RestfulSimplifiedPeriodApplicationKeyValue|extjs_model }};

    
{% endblock %}

{% block onready %}
    {{ block.super }}
    Ext.create('Ext.container.Viewport', {
        layout: 'fit',
        layout: 'border',
        items: [{
            region: 'north',
            xtype: 'pageheader',
            navclass: 'administrator'
        }, {
            region: 'south',
            xtype: 'pagefooter'
        }, {
            xtype: 'statistics-periodadminlayout',
            region: 'center',
            margin: {left: 10, right: 10},
            periodid: {{ periodid }}
        }]
    });
{% endblock %}
