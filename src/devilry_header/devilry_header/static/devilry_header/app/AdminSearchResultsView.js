Ext.define('devilry_header.AdminSearchResultsView', {
    extend: 'devilry_header.BaseSearchResultsView',
    alias: 'widget.devilry_header_adminsearchresults',
    extraCls: 'devilry_header_adminsearchresults',

    singleResultTpl: [
        '<div><a href="#" class="result-target-link">{title}</a>',
            ' <span class="label label-inverse typename">{[this.getTypeName(values.type)]}</span>',
        '</div>',
        '<div class="muted"><small class="path">{path}</small></div>'
    ],

    heading: gettext('Content where you are admin')
});