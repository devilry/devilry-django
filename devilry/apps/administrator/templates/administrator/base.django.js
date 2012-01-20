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
        urlPrefix: DASHBOARD_URL,
        nodeRowTpl: '{{ restfulapi.RestfulSimplifiedNode.ExtjsModelMeta.combobox_tpl|escapejs }}',
        subjectRowTpl: '{{ restfulapi.RestfulSimplifiedSubject.ExtjsModelMeta.combobox_tpl|escapejs }}',
        periodRowTpl: '{{ restfulapi.RestfulSimplifiedPeriod.ExtjsModelMeta.combobox_tpl|escapejs }}',
        assignmentRowTpl: '{{ restfulapi.RestfulSimplifiedAssignment.ExtjsModelMeta.combobox_tpl|escapejs }}',
        assignmentgroupRowTpl: '{{ restfulapi.RestfulSimplifiedAssignmentGroup.ExtjsModelMeta.combobox_tpl|escapejs }}',
        deliveryRowTpl: '{{ restfulapi.RestfulSimplifiedDelivery.ExtjsModelMeta.combobox_tpl|escapejs }}'
    });
    searchwidget.loadInitialValues();
{% endblock %}
