/**
 * Search widget with a {@link devilry.administrator.MultiSearchField} on top
 * and results in a {@link devilry.administrator.MultiSearchResults} below.
 *
 *     Search: ______________
 *    
 *     |Result1             |
 *     +--------------------|
 *     |                    |
 *     |                    |
 *     |                    |
 *     +--------------------+
 *    
 *     |Result2             |
 *     +--------------------|
 *     |                    |
 *     |                    |
 *     |                    |
 *     +--------------------+
 *
 * @xtype administratorsearchwidget
 * @cfg {[Object]} searchResultItems Item list forwarded to the item config of {@link devilry.administrator.MultiSearchResults}
 * */
Ext.define('devilry.administrator.SearchWidget', {
    extend: 'Ext.container.Container',
    alias: 'widget.administratorsearchwidget',

    initComponent: function() {
        Ext.apply(this, {
            items: [{
                xtype: 'administratormultisearchfield'
            }, {
                xtype: 'administratormultisearchresults',
                items: this.searchResultItems
            }]
        });

        this.callParent(arguments);
    },

    focusOnSearchfield: function() {
        var searchfield = this.items.items[0];
        searchfield.focus();
    }
});
