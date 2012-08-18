{% extends "theme/common.django.html" %}
{% load extjs %}

{% block i18nimport %}
    <script type="text/javascript" src="{% url devilry_administrator_i18n %}"></script>
{% endblock %}

{% block appjs %}
    {{ block.super }}
    var DASHBOARD_URL = '{{ DEVILRY_URLPATH_PREFIX }}/administrator/';
{% endblock %}
