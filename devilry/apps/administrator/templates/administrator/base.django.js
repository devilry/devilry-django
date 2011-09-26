{% extends "theme/common.django.html" %}
{% load extjs %}

{% block imports %}
    {{ block.super }}
    Ext.require('devilry.extjshelpers.page.Header');
    Ext.require('devilry.extjshelpers.page.Footer');
{% endblock %}

{% block appjs %}
    var DASHBOARD_URL = '{{ DEVILRY_URLPATH_PREFIX }}/administrator/';

    {% for RestfulCls in restfulapi.values %}
        {{ RestfulCls|extjs_combobox_model:"Search" }};
        {{ RestfulCls|extjs_store:"Search" }};
    {% endfor %}
{% endblock %}

{% block onready %}
    {{ block.super }}
    Ext.getBody().mask("Loading page", 'page-load-mask');

    var searchwidget = Ext.create('devilry.administrator.AdministratorSearchWidget', {
        //renderTo: 'searchwidget-container',
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


{% comment %}
{% block body2 %}
<div class="section" id="searchsection" style="{% block searchsectionstyle %}{% endblock %}">
    <div id='searchwidget-container'></div>
    <p class='searchwidget-help'>In the box above, you can search for anything
    related to anything that you have permission to view or edit as an
    <strong>administrator</strong>. Searching for a user will find any item related
    to that user, and searching for a subject will find anything related to that
    subject.</p>
</div>
{% endblock %}
{% endcomment %}
