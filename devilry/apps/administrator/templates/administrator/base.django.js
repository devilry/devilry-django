{% extends "theme/common.django.html" %}
{% load extjs %}

{% block appjs %}
    {{ block.super }}
    var DASHBOARD_URL = '{{ DEVILRY_URLPATH_PREFIX }}/administrator/';
{% endblock %}
