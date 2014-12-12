/**
 * Search results for many results, each result shown in a
 * {@link devilry.extjshelpers.searchwidget.SearchResults}.
 * */
Ext.define('devilry.extjshelpers.searchwidget.MultiSearchResults', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.multisearchresults',
    cls: 'multisearchresults',
    autoScroll: true,
    
    config: {
        searchWidget: undefined
    }
});
