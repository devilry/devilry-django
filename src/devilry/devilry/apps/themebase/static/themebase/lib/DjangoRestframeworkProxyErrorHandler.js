/**
 * Adds utilites for ``djangorestframework`` errors,
 */
Ext.define('themebase.DjangoRestframeworkProxyErrorHandler', {
    extend: 'themebase.ProxyErrorHandler',

    _decodeResponseTextJSON: function(response) {
        try {
            return Ext.JSON.decode(response.responseText);
        } catch(e) {
            return null;
        }
    },

    _addFieldErrors: function(responseData) {
        if(responseData.field_errors) {
            this.fielderrors = responseData.field_errors;
        }
    },

    _addMessages: function(responseData) {
        if(responseData.detail) {
            this.errormessages.push(responseData.detail);
        }
        if(responseData.messages) {
            this.errormessages = this.errormessages.concat(responseData.messages);
        }
    },

    /**
     * Add errors from an extjs response object (such as the one given to proxy
     * exception events) on the format produced by the python function
    * ``devilry.rest.errorhandlers.create_errordict``.
     */
    addRestErrorsFromResponse: function(response) {
        var responseData = this._decodeResponseTextJSON(response);
        if(responseData) {
            this._addMessages(responseData);
            this._addFieldErrors(responseData);
        }
    },

    addErrors: function(response, operation) {
        this.addRestErrorsFromResponse(response);
        if(!this.hasErrors()) {
            this.addErrorsFromOperation(operation);
        }
    }
});
