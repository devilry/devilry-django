{% extends "administrator/base.django.js" %}
{% load extjs %}

{% block imports %}
    {{ block.super }}
    Ext.require([
        'devilry.administrator.node.Layout',
        //'devilry.administrator.NodeBrowser'
    ]);
{% endblock %}


{% block appjs %}
    {{ block.super }}
    {{ restfulapi.RestfulSimplifiedSubject|extjs_model:";List" }};
    {{ restfulapi.RestfulSimplifiedNode|extjs_model:";List" }};
{% endblock %}

{% block onready %}
    {{ block.super }}

    Ext.getBody().unmask();
    Ext.create('Ext.container.Viewport', {
        layout: 'border',
        style: 'background-color: transparent',
        items: [{
            region: 'north',
            xtype: 'pageheader',
            navclass: 'administrator'
        }, {
            region: 'south',
            xtype: 'pagefooter'
        }, {
            region: 'center',
            xtype: 'administrator-nodelayout',
            nodeid: {{ objectid }},
            padding: {left: 20, right: 20}
        }]
    });

    {% comment %}
    Ext.widget('window', {
        layout: 'fit',
        width: 500,
        height: 400,
//        items: [Ext.create('devilry.administrator.NodeBrowser')]
        items: [Ext.create('devilry.administrator.NodeTree')]
    }).show();
    {% endcomment %}
{% endblock %}
