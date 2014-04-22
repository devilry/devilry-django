Ext.define('devilry_header.AdminSearchResultsView', {
    extend: 'devilry_header.BaseSearchResultsView',
    alias: 'widget.devilry_header_adminsearchresults',
    extraCls: 'devilry_header_adminsearchresults',

    singleResultTpl: [
        '<div><a href="{[this.getUrl(values)]}" class="{[this.getResultLinkCls()]}">{title}</a>',
            ' <span class="label label-inverse typename">{[this.getTypeName(values.type)]}</span>',
        '</div>',
        '<div class="meta path">{path}</div>',
        '<tpl if="type == \'core_assignmentgroup\'">',
            '<div class="meta students">',
                '{[this.joinStringArray(values.students)]}',
            '</small></div>',
        '</tpl>'
    ],

    heading: gettext('Content where you are admin'),


    getUrl:function (values) {
        var subjectadmin_prefix = Ext.String.format('{0}/devilry_subjectadmin/',
            window.DevilrySettings.DEVILRY_URLPATH_PREFIX);
        var nodeadmin_prefix = Ext.String.format('{0}/devilry_nodeadmin/',
            window.DevilrySettings.DEVILRY_URLPATH_PREFIX);
        if(values.type === 'core_assignmentgroup') {
            return Ext.String.format('{0}#/assignment/{1}/@@manage-students/@@select/{2}',
                subjectadmin_prefix, values.assignment_id, values.id);
        } else if(values.type === 'core_assignment') {
            return Ext.String.format('{0}#/assignment/{1}/',
                subjectadmin_prefix, values.id);
        } else if(values.type === 'core_period') {
            return Ext.String.format('{0}#/period/{1}/',
                subjectadmin_prefix, values.id);
        } else if(values.type === 'core_subject') {
            return Ext.String.format('{0}#/subject/{1}/',
                subjectadmin_prefix, values.id);
        } else if(values.type === 'core_node') {
            return Ext.String.format('{0}#/node/{1}',
                nodeadmin_prefix, values.id);
        } else {
            throw Ext.String.format('Unknown type: {0}', values.type);
        }
    }
});