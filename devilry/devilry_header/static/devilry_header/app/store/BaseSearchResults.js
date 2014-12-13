Ext.define('devilry_header.store.BaseSearchResults', {
    extend: 'Ext.data.Store',

    search: function (params, loadConfig) {
        Ext.apply(this.proxy.extraParams, params);
        this.load(loadConfig);
    }
});