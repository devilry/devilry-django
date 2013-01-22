{% extends "examiner/base.django.js" %}
{% load extjs %}

{% block imports %}
    {{ block.super }}
    Ext.require([
        'devilry.examiner.Dashboard',
    ]);
{% endblock %}

{% block appjs %}
    {{ block.super }}
{% endblock %}


{% block onready %}
    Ext.create('Ext.container.Viewport', {
        layout: 'border',
        style: 'background-color: transparent',
        items: [{
            region: 'north',
            xtype: 'devilryheader',
            navclass: 'examiner'
        }, {
            region: 'center',
            xtype: 'examiner-dashboard',
            dashboardUrl: DASHBOARD_URL,
            padding: '10 40 20 40',
            margin: 0,
            border: false
        }]
    });
{% endblock %}
