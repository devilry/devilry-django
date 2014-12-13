/**
 * Adds utilites for ``djangorestframework`` errors,
 */
Ext.define('devilry_extjsextras.DjangoRestframeworkProxyErrorHandler', {
    extend: 'devilry_extjsextras.ProxyErrorHandler',

    _decodeResponseTextJSON: function(response) {
        try {
            return Ext.JSON.decode(response.responseText);
        } catch(e) {
            return null;
        }
    },

    _addFieldErrors: function(responseData) {
        if(!Ext.isEmpty(responseData.field_errors)) {
            this.fielderrors = responseData.field_errors;
        }
    },

    _addMessages: function(responseData) {
        if(responseData.detail) {
            this.errormessages.push(responseData.detail);
        }
        if(responseData.errors) {
            this.errormessages = this.errormessages.concat(responseData.errors);
        }
    },

    /**
     * Add errors from an extjs response object (such as the one given to proxy
     * exception events).
     */
    addRestErrorsFromResponse: function(response) {
        var responseData = this._decodeResponseTextJSON(response);
        if(responseData) {
            this._addMessages(responseData);
            this._addFieldErrors(responseData);
        }
    },

    addErrors: function(response, operation) {
        if(response) {
            this.addRestErrorsFromResponse(response);
        }
        if(!this.hasErrors()) {
            this.addErrorsFromOperation(operation);
        }
    },

    addBatchErrors: function(batch) {
        Ext.Array.each(batch.exceptions, function(exception) {
            var message = this.parseHttpError(exception.error, exception.request);
            this.errormessages.push(message);
        }, this);
    }
});
