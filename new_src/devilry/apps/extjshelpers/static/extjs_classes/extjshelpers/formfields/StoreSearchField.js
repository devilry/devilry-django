Ext.define('devilry.extjshelpers.formfields.StoreSearchField', {
    extend: 'devilry.extjshelpers.SearchField',
    alias: 'widget.storesearchfield',
    requires: [
        'devilry.extjshelpers.SearchStringParser'
    ],

    /**
     * @cfg
     * An ``Ext.dat.Store``.
     */
    store: undefined,

    /**
     * @cfg
     * Forwarded to {@link devilry.extjshelpers.SearchStringParser#applyToExtraParams}.
     */
    shortcuts: undefined,

    /**
     * @cfg
     * Forwarded to SearchStringParser.
     */
    alwaysAppliedFilters: undefined,

    /**
     * @cfg {bool} [autoLoadStore]
     */
    autoLoadStore: true,

    /**
     * @cfg {int} [pageSize]
     */
    pageSize: 10,

    constructor: function(config) {
        this.callParent(arguments);
    },

    initComponent: function() {
        this.addListener('newSearchValue', this.onNewSearchValue, this);
        this.addListener('emptyInput', this.onEmptyInput, this);
        this.callParent(arguments);
        if(this.autoLoadStore) {
            this.onEmptyInput();
        };
    },

    onNewSearchValue: function(value) {
        var parsedValue = Ext.create('devilry.extjshelpers.SearchStringParser', {
            pageSizeWithoutType: this.pageSize,
            searchstring: value,
            alwaysAppliedFilters: this.alwaysAppliedFilters
        });

        parsedValue.applyPageSizeToStore(this.store);
        parsedValue.applyToExtraParams(this.store.proxy.extraParams, this.shortcuts);
        this.store.load();
    },

    refreshStore: function() {
        this.onNewSearchValue(this.getValue());
    },

    onEmptyInput: function() {
        this.onNewSearchValue('');
    }
});
