{% extends "theme/common.django.html" %}
{% load extjs %}

{% block imports %}
    {{ block.super }}
    Ext.require('devilry.extjshelpers.searchwidget.SearchWidget');
    Ext.require('devilry.extjshelpers.searchwidget.FilterConfigDefaults');
{% endblock %}

{% block appjs %}
    {{ block.super }}
    var DASHBOARD_URL = '{{ DEVILRY_URLPATH_PREFIX }}/examiner/';

    {{ restfulapi.RestfulSimplifiedAssignment|extjs_combobox_model:"Search" }};
    {{ restfulapi.RestfulSimplifiedAssignmentGroup|extjs_combobox_model:"Search" }};
    {{ restfulapi.RestfulSimplifiedDelivery|extjs_combobox_model:"Search" }};

    var assignmentstore = {{ restfulapi.RestfulSimplifiedAssignment|extjs_store:"Search" }};
    var assignmentgroupstore = {{ restfulapi.RestfulSimplifiedAssignmentGroup|extjs_store:"Search" }};
    var deliverystore = {{ restfulapi.RestfulSimplifiedDelivery|extjs_store:"Search" }};
    var DASHBOARD_URL = '{{ DEVILRY_URLPATH_PREFIX }}/examiner/';
{% endblock %}

{% block onready %}
    {{ block.super }}
    var searchwidget = Ext.create('devilry.extjshelpers.searchwidget.SearchWidget', {
        hidden: true,
        searchResultItems: [{
            xtype: 'searchresults',
            title: 'Deliveries',
            store: deliverystore,
            filterconfig: devilry.extjshelpers.searchwidget.FilterConfigDefaults.delivery,
            resultitemConfig: {
                tpl: '{{ restfulapi.RestfulSimplifiedDelivery.ExtjsModelMeta.combobox_tpl|escapejs }}',
                defaultbutton: {
                    text: 'View',
                    clickLinkTpl: DASHBOARD_URL + 'assignmentgroup/{deadline__assignment_group}?deliveryid={id}'
                }
            }
        }, {
            xtype: 'searchresults',
            title: 'Assignment groups',
            store: assignmentgroupstore,
            filterconfig: devilry.extjshelpers.searchwidget.FilterConfigDefaults.assignmentgroup,
            resultitemConfig: {
                tpl: '{{ restfulapi.RestfulSimplifiedAssignmentGroup.ExtjsModelMeta.combobox_tpl|escapejs }}',
                defaultbutton: {
                    text: 'View/edit',
                    clickLinkTpl: DASHBOARD_URL + 'assignmentgroup/{id}'
                },
                menuitems: [{
                    text: 'Show deliveries',
                    clickFilter: 'type:delivery group:{id}'
                }]
            }
        }, {
            xtype: 'searchresults',
            title: 'Assignments',
            store: assignmentstore,
            filterconfig: devilry.extjshelpers.searchwidget.FilterConfigDefaults.assignment,
            resultitemConfig: {
                tpl: '{{ restfulapi.RestfulSimplifiedAssignment.ExtjsModelMeta.combobox_tpl|escapejs }}',
                defaultbutton: {
                    text: 'View',
                    clickLinkTpl: DASHBOARD_URL + 'assignment/{id}'
                },
                menuitems: [{
                    text: 'Show groups',
                    clickFilter: 'type:group assignment:{id}'
                }, {
                    text: 'Show deliveries',
                    clickFilter: 'type:delivery assignment:{id}'
                }]
            }
        }]
    });

{% endblock %}
