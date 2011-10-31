{% extends "theme/common.django.html" %}

{% block appjs %}
    {{ block.super }}
    Ext.require([
        'devilry.extjshelpers.assignmentgroup.DeliveriesOnSingleGroupLoader',
        'devilry.extjshelpers.RestProxy'
    ]);
{% endblock %}

{% block onready %}
    {{ block.super }}
    Ext.getBody().unmask();

    Ext.create('devilry.extjshelpers.assignmentgroup.DeliveriesOnSingleGroupLoader', {
        assignmentgroup_id: 52
    });
{% endblock %}
