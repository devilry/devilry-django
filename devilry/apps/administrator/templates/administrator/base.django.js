{% extends "theme/common.django.html" %}
{% load extjs %}

{% block appjs %}
    {{ block.super }}
    var DASHBOARD_URL = '{{ DEVILRY_URLPATH_PREFIX }}/administrator/';

{% endblock %}

{% block onready %}
    {{ block.super }}
    var searchwidget = Ext.create('devilry.administrator.AdministratorSearchWidget', {
        //renderTo: 'searchwidget-container',
        hidden: true,
        urlPrefix: DASHBOARD_URL
    });
    searchwidget.loadInitialValues();
{% endblock %}
