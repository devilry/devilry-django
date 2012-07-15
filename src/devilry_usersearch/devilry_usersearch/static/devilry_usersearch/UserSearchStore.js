Ext.define('devilry_usersearch.UserSearchStore', {
    extend: 'Ext.data.Store',
    model: 'devilry_usersearch.UserSearchModel',

    search: function(query, callbackFn, callbackScope) {
        this.proxy.extraParams.query = query;
        this.load({
            scope: callbackScope,
            callback: callbackFn
        });
    }
});
