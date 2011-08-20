Ext.define('devilry.extjshelpers.formfields.StoreSearchField', {
    extend: 'devilry.extjshelpers.SearchField',
    alias: 'widget.storesearchfield',
    requires: [
        'devilry.extjshelpers.SearchStringParser'
    ],

    config: {
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

        autoLoad: true
    },

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
        this.addListener('newSearchValue', this.onNewSearchValue, this);
        this.addListener('emptyInput', this.onEmptyInput, this);

        if(this.autoLoad) {
            this.onEmptyInput();
        };
    },

    onNewSearchValue: function(value) {
        var parsedValue = Ext.create('devilry.extjshelpers.SearchStringParser', {
            pageSizeWithoutType: 10,
            searchstring: value,
            alwaysAppliedFilters: this.alwaysAppliedFilters
        });

        parsedValue.applyPageSizeToStore(this.store);
        parsedValue.applyToExtraParams(this.store.proxy.extraParams, this.shortcuts);
        this.store.load();
    },

    onEmptyInput: function() {
        this.onNewSearchValue('');
    }
});
