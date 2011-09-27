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
    {{ restfulapi.RestfulSimplifiedAssignmentGroup|extjs_combobox_model:"Search" }};
    {{ restfulapi.RestfulSimplifiedAssignmentGroup|extjs_store:"Search" }};
    {{ restfulapi.RestfulSimplifiedDeadline|extjs_combobox_model:"Search" }};
    {{ restfulapi.RestfulSimplifiedDeadline|extjs_store:"Search" }};
    {{ restfulapi.RestfulSimplifiedDelivery|extjs_combobox_model:"Search" }};
    {{ restfulapi.RestfulSimplifiedDelivery|extjs_store:"Search" }};
{% endblock %}

{% block onready %}
    {{ block.super }}

    var searchwidget = Ext.create('devilry.student.StudentSearchWidget', {
        urlPrefix: DASHBOARD_URL,
        assignmentgroupRowTpl: '{{ restfulapi.RestfulSimplifiedAssignmentGroup.ExtjsModelMeta.combobox_tpl|escapejs }}',
        deadlineRowTpl: '{{ restfulapi.RestfulSimplifiedDeadline.ExtjsModelMeta.combobox_tpl|escapejs }}',
        deliveryRowTpl: '{{ restfulapi.RestfulSimplifiedDelivery.ExtjsModelMeta.combobox_tpl|escapejs }}'
    });
{% endblock %}
