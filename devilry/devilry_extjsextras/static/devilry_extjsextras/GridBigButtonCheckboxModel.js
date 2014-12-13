/**
 * */
Ext.define('devilry_extjsextras.GridBigButtonCheckboxModel', {
    extend: 'Ext.selection.CheckboxModel',

    headerWidth: 50, // The width of the checkbox column

    /**
     * Configuration for the header cell (the cell where you can select/deselect all)
     */
    getHeaderConfig: function() {
        var config = this.callParent(arguments);
        if(config.cls !== '') { // If we do not have a header, cls will be empty, and we should keep it that way
            config.cls += ' ' + 'devilry-column-header-checkbox-bigbutton';
        }
        return config;
    },
    
    /**
     * Called to render the cells containing the checkbox for each row.
     * The same as the superclass, but we add our own css class.
     */
    renderer: function(value, metaData, record, rowIndex, colIndex, store, view) {
        var baseCSSPrefix = Ext.baseCSSPrefix;
        metaData.tdCls = baseCSSPrefix + 'grid-cell-special ' + baseCSSPrefix + 'grid-cell-row-checker devilry-grid-cell-row-checker-bigbutton';
        return '<div class="' + baseCSSPrefix + 'grid-row-checker">&#160;</div>';
    }
});
