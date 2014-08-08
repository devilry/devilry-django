Ext.define('devilry_header.ExaminerSearchResultsView', {
    extend: 'devilry_header.BaseSearchResultsView',
    alias: 'widget.devilry_header_examinersearchresults',
    extraCls: 'devilry_header_examinersearchresults',

    singleResultTpl: [
        '<div>',
            '<a href="{[this.getUrl(values)]}" class="{[this.getResultLinkCls()]}">{title}</a>',
            ' <span class="label label-inverse typename">{[this.getTypeName(values.type)]}</span>',
        '</div>',
        '<div class="meta path">{path}</div>',
        '<tpl if="type == \'core_assignmentgroup\'">',
            '<div class="meta students">',
                '{[this.joinStringArray(values.students)]}',
            '</small></div>',
        '</tpl>'
    ],

    heading: gettext('Content where you are examiner'),

    getUrl:function (values) {
        var prefix = Ext.String.format('{0}/examiner/',
            window.DevilrySettings.DEVILRY_URLPATH_PREFIX);
        if(values.type === 'core_assignmentgroup') {
            return Ext.String.format('{0}assignmentgroup/{1}',
                prefix, values.id);
        } else if(values.type === 'core_assignment') {
            return Ext.String.format('{0}assignment/{1}',
                prefix, values.id);
        } else {
            throw Ext.String.format('Unknown type: {0}', values.type);
        }
    }
});