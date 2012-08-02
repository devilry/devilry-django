{% extends "administrator/base.django.js" %}
{% load extjs %}

{% block imports %}
    {{ block.super }}
    Ext.require([
        'devilry.administrator.subject.Layout'
    ]);
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
            navclass: 'administrator'
        }, {
            region: 'south',
            xtype: 'pagefooter'
        }, {
            region: 'center',
            xtype: 'administrator-subjectlayout',
            subjectid: {{ objectid }},
            padding: '0 20 0 20'
        }]
    });
{% endblock %}
