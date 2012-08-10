{% extends "theme/common.django.html" %}
{% load extjs %}


{% block i18nimport %}
    <script type="text/javascript" src="{% url devilry_student_i18n %}"></script>
{% endblock %}

{% block imports %}
    {{ block.super }}
    Ext.require('devilry.extjshelpers.searchwidget.SearchWidget');
    Ext.require('devilry.extjshelpers.searchwidget.FilterConfigDefaults');
{% endblock %}

{% block appjs %}
    {{ block.super }}
    var DASHBOARD_URL = '{{ DEVILRY_URLPATH_PREFIX }}/student/';
{% endblock %}
