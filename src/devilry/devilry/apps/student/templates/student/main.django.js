{% extends "student/base.django.js" %}
{% load extjs %}

{% block imports %}
    {{ block.super }}
    Ext.require('devilry.student.Dashboard');
{% endblock %}


{% block onready %}
    {{ block.super }}
    Ext.getBody().unmask();
    Ext.create('Ext.container.Viewport', {
        layout: 'border',
        style: 'background-color: transparent',
        items: [{
            region: 'north',
            xtype: 'devilryheader',
            navclass: 'student'
        }, {
            region: 'south',
            xtype: 'pagefooter'
        }, {
            region: 'center',
            xtype: 'student-dashboard',
            dashboardUrl: DASHBOARD_URL,
            padding: '0 20 0 20',
            border: false
        }]
    });
{% endblock %}
