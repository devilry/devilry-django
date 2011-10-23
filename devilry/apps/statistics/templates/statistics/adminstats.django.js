{% extends "theme/common.django.html" %}
{% load extjs %}

{% block imports %}
    {{ block.super }}
    Ext.require('devilry.statistics.PeriodAdminLayout');
{% endblock %}

{% block appjs %}
    {{ RestfulSimplifiedPeriod|extjs_model:"subject" }};
    {{ RestfulSimplifiedRelatedStudent|extjs_model:"user_details" }}
    {{ RestfulSimplifiedRelatedStudentKeyValue|extjs_model }}
    {{ RestfulSimplifiedAssignment|extjs_model }};
    {{ RestfulSimplifiedAssignmentGroup|extjs_model:"users,feedback" }};

    
{% endblock %}

{% block onready %}
    {{ block.super }}
    Ext.create('devilry.statistics.PeriodAdminLayout', {
        periodid: {{ periodid }}
    });
{% endblock %}
