Ext.define('devilry_header.StudentSearchResultsView', {
    extend: 'devilry_header.BaseSearchResultsView',
    alias: 'widget.devilry_header_studentsearchresults',
    extraCls: 'devilry_header_studentsearchresults',

    singleResultTpl: [
        '<div><a href="#" class="result-target-link">{title}</a></div>',
        '<div class="muted"><small class="path">{path}</small></div>'
    ],

    heading: gettext('Content where you are student')
});