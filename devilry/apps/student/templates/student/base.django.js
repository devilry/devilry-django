{% extends "theme/common.django.html" %}
{% load extjs %}

{% block imports %}
    {{ block.super }}
    Ext.require('devilry.extjshelpers.searchwidget.SearchWidget');
    Ext.require('devilry.extjshelpers.searchwidget.FilterConfigDefaults');
{% endblock %}

{% block appjs %}
    {{ block.super }}
    var DASHBOARD_URL = '{{ DEVILRY_URLPATH_PREFIX }}/student/';
{% endblock %}

{% block onready %}
    {{ block.super }}

    var searchwidget = Ext.create('devilry.student.StudentSearchWidget', {
        urlPrefix: DASHBOARD_URL,
        hidden: true
    });
{% endblock %}
