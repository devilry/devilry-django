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
    style: {
        'box-shadow': '0 3px 8px #888'
    },
    margin: {
        bottom: 40
    }
});
