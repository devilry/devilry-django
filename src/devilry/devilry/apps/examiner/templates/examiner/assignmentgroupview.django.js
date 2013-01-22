{% extends "examiner/base.django.js" %}

{% block extra_js_libraries %}
    {% include "markup/mathjaxheader.django.html" %}
{% endblock %}

{% block imports %}
    {{ block.super }}
    Ext.require('devilry.extjshelpers.assignmentgroup.AssignmentGroupOverview');
{% endblock %}

{% block onready %}
    {{ block.super }}

    Ext.getBody().unmask();

    Ext.create('Ext.container.Viewport', {
        layout: 'border',
        style: 'background-color: transparent',
        items: [{
            region: 'north',
            xtype: 'devilryheader',
            navclass: 'examiner'
        }, {
            region: 'center',
            xtype: 'assignmentgroupoverview',
            assignmentgroupid: {{ objectid }},
            isAdministrator: false,
            canExamine: true,
            padding: '0 20 0 20',
            listeners: {
                assignmentGroupLoaded: function(groupRecord) {
                    var path = [
                        groupRecord.get('parentnode__parentnode__parentnode__short_name'),
                        groupRecord.get('parentnode__parentnode__short_name'),
                        groupRecord.get('parentnode__short_name')].join('.');
                    var groupmemebers = [];
                    Ext.Array.each(groupRecord.get('candidates'), function(candidate) {
                        groupmemebers.push(candidate.full_name || candidate.identifier);
                    }, this);
                    var groupIdent = groupmemebers.join(', ');
                    if(groupRecord.get('name')) {
                        groupIdent = Ext.String.format('{0}: {1}', groupRecord.get('name'), groupIdent);
                    }
                    if(Ext.String.trim(groupIdent) == '') {
                        groupIdent = groupRecord.get('id');
                    }
                    devilry_header.Breadcrumbs.getInBody().set([{
                        text: path,
                        url: Ext.String.format('../assignment/{0}', groupRecord.get('parentnode'))
                    }, {
                        text: gettext('Students'),
                        url: Ext.String.format('../assignment/{0}#students', groupRecord.get('parentnode'))
                    }], groupIdent);
                    window.document.title = Ext.String.format('{0} - Devilry', groupIdent);
                }
            }
        }]
    });
{% endblock %}
