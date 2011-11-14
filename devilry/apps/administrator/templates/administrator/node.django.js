{% extends "administrator/single-base.django.html" %}
{% load extjs %}

{% block title %}Node - {{ block.super }}{% endblock %}

{% block headextra %}
{{ block.super }}

<script>
    {{ restfulapi.RestfulSimplifiedNode|extjs_model:"admins" }}
    {{ restfulapi.RestfulSimplifiedSubject|extjs_model:"admins" }}
    {{ restfulapi.RestfulSimplifiedPeriod|extjs_model:"subject,admins" }}
    {{ restfulapi.RestfulSimplifiedPeriodApplicationKeyValue|extjs_model }}

    Ext.require('devilry.administrator.node.PrettyView');
    Ext.require('devilry.extjshelpers.RestfulSimplifiedEditPanel');
    Ext.require('devilry.extjshelpers.forms.administrator.Node');
    Ext.onReady(function() {
        var prettyview = Ext.create('devilry.administrator.node.PrettyView', {
            renderTo: 'content-main',
            modelname: {{ restfulapi.RestfulSimplifiedNode|extjs_modelname }},
            objectid: {{ objectid }},
            dashboardUrl: DASHBOARD_URL
        });

        var heading = Ext.ComponentManager.create({
            xtype: 'component',
            renderTo: 'content-heading',
            data: {},
            tpl: [
                '<h1>{long_name} ({short_name})</h1>'
            ]
        });

        function showEditWindow(record, button) {
            var editpanel = Ext.ComponentManager.create({
                xtype: 'restfulsimplified_editpanel',
                model: {{ restfulapi.RestfulSimplifiedNode|extjs_modelname }},
                editform: Ext.widget('administrator_nodeform'),
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
        }

        prettyview.addListener('edit', showEditWindow);
        prettyview.addListener('loadmodel', function(record) {
            heading.update(record.data);
            //showEditWindow(record);
        });
    });
</script>
{% endblock %}
