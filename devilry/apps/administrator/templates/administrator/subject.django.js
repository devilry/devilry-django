{% extends "administrator/base.django.js" %}
{% load extjs %}

{% block imports %}
    {{ block.super }}
    Ext.require([
        'devilry.administrator.subject.Layout'
    ]);
{% endblock %}


{% block appjs %}
    {{ block.super }}
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
            xtype: 'administrator-subjectlayout',
            subjectid: {{ objectid }},
            padding: {left: 20, right: 20}
        }]
    });
{% endblock %}
