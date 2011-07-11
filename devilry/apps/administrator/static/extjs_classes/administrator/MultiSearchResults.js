/**
 * Search results for many results, each result shown in a
 * {@link devilry.administrator.SearchResults}.
 *
 * @xtype administratormultisearchresults
 * Integrates with {@link devilry.administrator.MultiSearchField}.
 * */
Ext.define('devilry.administrator.MultiSearchResults', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.administratormultisearchresults',
    id: 'floating-searchresult',
    floating: true,
    cls: 'search-popup-panel'
});
