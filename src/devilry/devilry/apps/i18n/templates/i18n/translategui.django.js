{% extends "theme/common.django.html" %}
{% load extjs %}

{% block imports %}
    {{ block.super }}
    Ext.require('devilry.i18n.TranslateGui');
{% endblock %}

{% block onready %}
    //Ext.getBody().unmask();
    Ext.create('Ext.container.Viewport', {
        layout: 'fit',
        items: {
            xtype: 'i18n-translategui'
        }
    });
{% endblock %}
