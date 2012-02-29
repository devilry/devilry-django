/**
 * Adds utilites for ``devilry.extjshelpers.RestProxy`` error handling.
 */
Ext.define('themebase.RestfulApiProxyErrorHandler', {
    extend: 'themebase.ProxyErrorHandler',

    /**
     * Adds the errors messages contained in the ``responseData`` added to
     * ``Ext.data.Operation`` objects by
     * ``devilry.extjshelpers.RestProxy.setException``.
     */
    addRestfulErrorsFromOperation: function(operation) {
        if(operation.responseData && operation.responseData.items) {
            var errors = operation.responseData.items;
            this.errormessages = errors.errormessages;
            this.fielderrors = this.removeGlobalFromFieldErrors(errors.fielderrors);
            return true;
        } else {
            return false;
        }
    },

    /** Copy fielderrors excluding any ``__all__`` attribute. */
    _removeGlobalFromFieldErrors: function(fielderrors) {
        var cleanedFieldErrors = {};
        Ext.Object.each(fielderrors, function(key, value) {
            if(key != '__all__') {
                cleanedFieldErrors[key] = value;
            }
        });
        return cleanedFieldErrors;
    }

    addErrors: function(response, operation) {
        if(!this.addRestfulErrorsFromOperation(response)) {
            this.addErrorsFromOperation(operation);
        }
    }
});
