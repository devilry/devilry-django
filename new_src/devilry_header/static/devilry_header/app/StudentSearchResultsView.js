Ext.define('devilry_header.StudentSearchResultsView', {
    extend: 'devilry_header.BaseSearchResultsView',
    alias: 'widget.devilry_header_studentsearchresults',
    extraCls: 'devilry_header_studentsearchresults',

    singleResultTpl: [
        '<div><a href="{[this.getUrl(values)]}" class="{[this.getResultLinkCls()]}">{title}</a></div>',
        '<div class="meta path">{path}</div>',
        '<tpl if="type == \'core_assignmentgroup\'">',
            '<tpl if="values.students.length &gt; 1">',
                '<div class="meta students">',
                    '{[this.joinStringArray(values.students)]}',
                '</small></div>',
            '</tpl>',
        '</tpl>'
    ],

    heading: gettext('Content where you are student'),

    getUrl:function (values) {
        var prefix = Ext.String.format('{0}/devilry_student/',
            window.DevilrySettings.DEVILRY_URLPATH_PREFIX);
        if(values.type === 'core_assignmentgroup') {
            return Ext.String.format('{0}#/group/{1}/',
                prefix, values.id);
        } else {
            throw Ext.String.format('Unknown type: {0}', values.type);
        }
    }
});