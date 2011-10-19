{% extends "theme/common.django.html" %}
{% load extjs %}

{% block imports %}
    {{ block.super }}
    Ext.require('devilry.statistics.PeriodAdminLayout');
{% endblock %}

{% block appjs %}
    {{ RestfulSimplifiedRelatedStudent|extjs_model:"user_details" }}
    var relatedstudent_store = {{ RestfulSimplifiedRelatedStudent|extjs_store }}
    {{ RestfulSimplifiedRelatedStudentKeyValue|extjs_model }}
    var relatedstudentkeyvalue_store = {{ RestfulSimplifiedRelatedStudentKeyValue|extjs_store }}
    var period_model = {{ RestfulSimplifiedPeriod|extjs_model }};
    var assignment_model = {{ RestfulSimplifiedAssignment|extjs_model }};
    var assignment_store = {{ RestfulSimplifiedAssignment|extjs_store }};
    var assignmentgroup_model = {{ RestfulSimplifiedAssignmentGroup|extjs_model:"assignment,users,feedback" }};
    var assignmentgroup_store = {{ RestfulSimplifiedAssignmentGroup|extjs_store }};

    
{% endblock %}

{% block onready %}
    {{ block.super }}
    Ext.create('devilry.statistics.PeriodAdminLayout', {
        periodid: {{ periodid }}
    });
{% endblock %}
