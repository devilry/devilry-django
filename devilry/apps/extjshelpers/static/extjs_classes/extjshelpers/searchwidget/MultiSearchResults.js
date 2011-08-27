/**
 * Search results for many results, each result shown in a
 * {@link devilry.extjshelpers.searchwidget.SearchResults}.
 *
 * @xtype multisearchresults
 * Integrates with {@link devilry.extjshelpers.searchwidget.MultiSearchField}.
 * */
Ext.define('devilry.extjshelpers.searchwidget.MultiSearchResults', {
    extend: 'Ext.window.Window',
    alias: 'widget.multisearchresults',
    id: 'floating-searchresult',
    cls: 'multisearchresults multisearchresults-floating',
    closeAction: 'hide',
    plain: true,
    
    config: {
        searchWidget: undefined
    }
});
