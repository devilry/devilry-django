Ext.define('devilry_header.store.AdminSearchResults', {
    extend: 'Ext.data.Store',
    model: 'devilry_header.model.AdminSearchResult',

    search: function (params, loadConfig) {
        Ext.apply(this.proxy.extraParams, params);
        this.load(loadConfig);
    }
});