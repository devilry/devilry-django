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
 * */
Ext.define('devilry.administrator.SearchWidget', {
    extend: 'Ext.container.Container',
    alias: 'widget.administrator-searchwidget',
});
