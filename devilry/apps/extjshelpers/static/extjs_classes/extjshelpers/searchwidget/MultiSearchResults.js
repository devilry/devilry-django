/**
 * Search results for many results, each result shown in a
 * {@link devilry.extjshelpers.searchwidget.SearchResults}.
 *
 * @xtype multisearchresults
 * Integrates with {@link devilry.extjshelpers.searchwidget.MultiSearchField}.
 * */
Ext.define('devilry.extjshelpers.searchwidget.MultiSearchResults', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.multisearchresults',
    id: 'floating-searchresult',
    floating: true,
    cls: 'multisearchresults multisearchresults-floating'
});
