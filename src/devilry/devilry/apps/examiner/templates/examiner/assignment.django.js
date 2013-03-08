{% extends "examiner/base.django.js" %}
{% load extjs %}


{% block imports %}
    {{ block.super }}
    Ext.require('devilry.examiner.AssignmentLayout');
    Ext.require('devilry_extjsextras.FloatingAlertmessageList');
{% endblock %}

    
{% block onready %}
    {{ block.super }}


    window.getFloatingAlertMessageList = function() {
        return Ext.ComponentQuery.query('#examinerAssignmentLayoutWrapper floatingalertmessagelist#appAlertmessagelist')[0];
    }

    Ext.create('Ext.container.Viewport', {
        layout: 'border',
//        cls: 'viewport',
        style: 'background-color: transparent',
        items: [{
            region: 'north',
            xtype: 'devilryheader',
            navclass: 'examiner'
        }, {
            region: 'center',
            layout: 'fit',
            itemId: 'examinerAssignmentLayoutWrapper',
            items: [{
                xtype: 'floatingalertmessagelist',
                itemId: 'appAlertmessagelist'
            }, {
                xtype: 'examiner-assignmentlayout',
                margin: '0 0 0 0',
                padding: '0 20 0 20',
                assignmentid: {{ assignmentid }}
            }]
        }]
    });
{% endblock %}
