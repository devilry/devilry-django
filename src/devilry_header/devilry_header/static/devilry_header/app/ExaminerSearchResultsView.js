Ext.define('devilry_header.ExaminerSearchResultsView', {
    extend: 'devilry_header.BaseSearchResultsView',
    alias: 'widget.devilry_header_examinersearchresults',
    extraCls: 'devilry_header_examinersearchresults',

    singleResultTpl: [
        '<div><a href="#" class="result-target-link">{title}</a></div>',
        '<div class="muted"><small class="path">{path}</small></div>'
    ],

    heading: gettext('Content where you are examiner')
});