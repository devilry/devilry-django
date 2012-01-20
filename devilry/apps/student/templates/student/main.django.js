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
            xtype: 'pageheader',
            navclass: 'student'
        }, {
            region: 'south',
            xtype: 'pagefooter'
        }, {
            region: 'center',
            xtype: 'container',
            border: false,
            padding: {left: 20, right: 20},
            layout: {
                type: 'vbox',
                align: 'stretch'
            },
            items: [searchwidget, {xtype:'box', height: 20}, {
                xtype: 'panel',
                flex: 1,
                layout: 'fit',
                border: false,
                items: [{
                    xtype: 'student-dashboard'
                }]
            }]
        }]
    });
    searchwidget.show();
    //createGrids();
{% endblock %}
