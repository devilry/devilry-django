/**
 * Adds utilites for ``devilry.rest`` errors,
 */
Ext.define('themebase.RestApiProxyErrorHandler', {
    extend: 'themebase.ProxyErrorHandler',

    _decodeResponseTextJSON: function(response) {
        try {
            return Ext.JSON.decode(response.responseText);
        } catch(e) {
            return null;
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
            this.errormessages = responseData.errormessages;
            this.fielderrors = responseData.fielderrors;
            return true;
        } else {
            return false;
        }
    },

    addErrors: function(response, operation) {
        if(!this.addRestErrorsFromResponse(response)) {
            this.addErrorsFromOperation(operation);
        }
    }
});
