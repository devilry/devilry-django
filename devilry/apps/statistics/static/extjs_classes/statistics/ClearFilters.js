Ext.define('devilry.statistics.ClearFilters', {
    extend: 'Ext.button.Button',
    alias: 'widget.statistics-clearfilters',
    text: 'Clear filters',
    hidden: true,
    
    config: {
        loader: undefined
    },

    filterTipTpl: Ext.create('Ext.XTemplate',
        '<ul>',
        '<tpl for="filterDescriptions">',
        '   <li>{.}</li>',
        '</tpl>',
        '</ul>'
    ),
    
    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
        this.filterDescriptions = [];
        this.loader.on('filterApplied', this._onFilterApplied, this);
        this.loader.on('filterCleared', this._onFilterCleared, this);
    },
    
    initComponent: function() {
        Ext.apply(this, {
            listeners: {
                scope: this,
                click: this._onClick
            }
        });
        this.callParent(arguments);
    },

    _onClick: function() {
        this.loader.clearFilter();
    },

    _onFilterApplied: function(loader, description) {
        Ext.Array.include(this.filterDescriptions, description);
        if(this.tooltip) {
            this.tooltip.hide();
        }
        this.tooltip = Ext.create('Ext.tip.ToolTip', {
            title: 'Active filters',
            html: this.filterTipTpl.apply(this),
            anchor: 'left',
            target: this.getEl().id,
            width: 415,
            closable: true,
            dismissDelay: 10000,
            autoHide: true
        });
        this.show();
        this.tooltip.show();
    },
    _onFilterCleared: function(loader) {
        if(this.tooltip) {
            this.tooltip.hide();
        }
        this.filterDescriptions = [];
        this.hide();
    }
});
