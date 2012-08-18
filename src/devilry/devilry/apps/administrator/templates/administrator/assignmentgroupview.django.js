{% extends "administrator/base.django.js" %}


{% block extra_js_libraries %}
    {% include "markup/mathjaxheader.django.html" %}
{% endblock %}

{% block imports %}
    {{ block.super }}
    Ext.require([
        'devilry.extjshelpers.assignmentgroup.AssignmentGroupOverview',
        'devilry_header.Breadcrumbs'
    ]);
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
            navclass: 'administrator'
        }, {
            region: 'south',
            xtype: 'pagefooter'
        }, {
            region: 'center',
            xtype: 'assignmentgroupoverview',
            assignmentgroupid: {{ objectid }},
            isAdministrator: true,
            canExamine: true,
            padding: '0 20 0 20',
            listeners: {
                assignmentGroupLoaded: function(groupRecord) {
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
                        text: groupRecord.get('parentnode__parentnode__parentnode__short_name'),
                        url: '../subject/' + groupRecord.get('parentnode__parentnode__parentnode')
                    }, {
                        text: groupRecord.get('parentnode__parentnode__short_name'),
                        url: '../period/' + groupRecord.get('parentnode__parentnode')
                    }, {
                        text: groupRecord.get('parentnode__short_name'),
                        url: '../assignment/' + groupRecord.get('parentnode')
                    }, {
                        text: gettext('Students'),
                        url: '../assignment/' + groupRecord.get('parentnode') + '#students'
                    }], groupIdent);
                    window.document.title = Ext.String.format('{0} - Devilry', groupIdent);
                }
            }
        }]
    });
{% endblock %}
