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
            region: 'south',
            xtype: 'pagefooter'
        }, {
            region: 'center',
            xtype: 'examiner-dashboard',
            dashboardUrl: DASHBOARD_URL,
            padding: '0 20 0 20',
            border: false
        }]
    });
{% endblock %}
