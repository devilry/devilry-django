{% extends "student/base.django.js" %}

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
            navclass: 'student'
        }, {
            region: 'south',
            xtype: 'pagefooter'
        }, {
            region: 'center',
            xtype: 'assignmentgroupoverview',
            assignmentgroupid: {{ objectid }},
            isAdministrator: false,
            canExamine: false,
            padding: '0 20 0 20',
            listeners: {
                assignmentGroupLoaded: function(groupRecord) {
                    var periodpath = [
                        groupRecord.get('parentnode__parentnode__parentnode__short_name'),
                        groupRecord.get('parentnode__parentnode__short_name')].join('.');
                    devilry_header.Breadcrumbs.getInBody().set([{
                        text: gettext('Browse'),
                        url: Ext.String.format('{0}/devilry_student/#/browse/',
                            DevilrySettings.DEVILRY_URLPATH_PREFIX)
                    }, {
                        text: periodpath,
                        url: Ext.String.format('{0}/devilry_student/#/browse/{1}',
                            DevilrySettings.DEVILRY_URLPATH_PREFIX,
                            groupRecord.get('parentnode__parentnode'))
                    }], groupRecord.get('parentnode__short_name'));

                    var path = [periodpath, groupRecord.get('parentnode__short_name')].join('.');
                    window.document.title = Ext.String.format('{0} - Devilry', path);
                }
            }
        }]
    });
{% endblock %}
