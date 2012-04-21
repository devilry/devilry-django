{% extends "administrator/base.django.js" %}


{% block extra_js_libraries %}
    {% include "markup/mathjaxheader.django.html" %}
{% endblock %}

{% block imports %}
    {{ block.super }}
    Ext.require('devilry.extjshelpers.assignmentgroup.AssignmentGroupOverview');
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
            xtype: 'assignmentgroupoverview',
            assignmentgroupid: {{ objectid }},
            isAdministrator: true,
            canExamine: true,
            padding: {left: 20, right: 20}
        }]
    });
{% endblock %}
