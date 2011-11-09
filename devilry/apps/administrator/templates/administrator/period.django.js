{% extends "administrator/base.django.js" %}
{% load extjs %}

{% block imports %}
    {{ block.super }}
    Ext.require('devilry.administrator.period.PrettyView');
    Ext.require('devilry.extjshelpers.RestfulSimplifiedEditPanel');
    Ext.require('devilry.extjshelpers.forms.administrator.Period');
    Ext.require('devilry.statistics.PeriodAdminLayout');
{% endblock %}


{% block appjs %}
    {{ block.super }}
    {{ restfulapi.RestfulSimplifiedSubject|extjs_model }};
    {{ restfulapi.RestfulSimplifiedPeriod|extjs_model:"subject,admins" }};
    {{ restfulapi.RestfulSimplifiedRelatedStudent|extjs_model }};
    {{ restfulapi.RestfulSimplifiedRelatedStudentKeyValue|extjs_model }};
    {{ restfulapi.RestfulSimplifiedAssignment|extjs_model }};
    {{ restfulapi.RestfulSimplifiedAssignmentGroup|extjs_model:"feedback" }};
    {{ restfulapi.RestfulSimplifiedCandidate|extjs_model }};
    {{ restfulapi.RestfulSimplifiedPeriodApplicationKeyValue|extjs_model }};
{% endblock %}

{% block onready %}
    {{ block.super }}
    var prettyview = Ext.create('devilry.administrator.period.PrettyView', {
        flex: 1,
        title: 'Administer',
        modelname: {{ restfulapi.RestfulSimplifiedPeriod|extjs_modelname }},
        objectid: {{ objectid }},
        dashboardUrl: DASHBOARD_URL
    });

    var heading = Ext.ComponentManager.create({
        xtype: 'component',
        data: {},
        cls: 'section treeheading',
        tpl: [
            '<h1>{long_name}</h1>',
            '<h2 class="endoflist">{parentnode__long_name}</h2>'
        ]
    });

    prettyview.addListener('loadmodel', function(record) {
        heading.update(record.data);
    });

    prettyview.addListener('edit', function(record, button) {
        var editpanel = Ext.ComponentManager.create({
            xtype: 'restfulsimplified_editpanel',
            model: {{ restfulapi.RestfulSimplifiedPeriod|extjs_modelname }},
            editform: Ext.widget('administrator_periodform'),
            record: record
        });
        var editwindow = Ext.create('devilry.administrator.DefaultEditWindow', {
            editpanel: editpanel,
            prettyview: prettyview,
            listeners: {
                scope: this,
                close: function() {
                    button.toggle(false);
                }
            }
        });
        editwindow.show();
        editwindow.alignTo(button, 'br', [-editwindow.getWidth(), 0]);
    });


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
            xtype: 'container',
            padding: {left: 20, right: 20},
            layout: {
                type: 'vbox',
                align: 'stretch'
            },
            items: [heading, {
                xtype: 'tabpanel',
                flex: 1,
                items: [{
                    title: 'Students',
                    xtype: 'statistics-periodadminlayout',
                    periodid: {{ objectid }},
                    hidesidebar: false,
                    defaultViewClsname: 'devilry.statistics.dataview.MinimalGridView'
                    //defaultViewClsname: 'devilry.statistics.dataview.FullGridView'
                }, prettyview]
            }]
        }]
    });
{% endblock %}
