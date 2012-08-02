{% extends "examiner/base.django.js" %}
{% load extjs %}


{% block imports %}
    {{ block.super }}
    Ext.require('devilry.examiner.AssignmentLayout');
{% endblock %}

    
{% block onready %}
    {{ block.super }}
    Ext.create('Ext.container.Viewport', {
        layout: 'border',
        cls: 'viewport',
        items: [{
            region: 'north',
            xtype: 'devilryheader',
            navclass: 'examiner'
        }, {
            region: 'south',
            xtype: 'pagefooter'
        }, {
            region: 'center',
            xtype: 'examiner-assignmentlayout',
            margin: '0 10 0 10',
            assignmentid: {{ assignmentid }}
        }]
    });
{% endblock %}
