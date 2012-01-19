Ext.define('devilry.i18n.MemoryStorageProxyWithExtraEvents', {
    extend: 'Ext.data.proxy.Memory',

    update: function(operation, callback, scope) {
        operation.setStarted();
        operation.setCompleted();
        operation.setSuccessful();

        if (typeof callback == 'function') {
            callback.call(scope || this, operation);
        }

    }
});
