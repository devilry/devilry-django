/**
 * Base class for proxy error handling.
 */
Ext.define('themebase.ProxyErrorHandler', {
    constructor: function() {
        this.errormessages = [];
        this.fielderrors = {};
    },


    /** Check if the list of errormessages and fielderrors are empty, and
     * return ``true`` if one of them contains at least one error message. */
    hasErrors: function() {
        return this.errormessages.length > 0 || Ext.Object.getSize(this.fielderrors) > 0;
    },

    /**
     * Add error from an ``Ext.data.Operation`` object. Uses
     * {@link #getErrorMessageFromOperation} to find the error message.
     *
     * @return The number of errors added.
     */
    addErrorsFromOperation: function(operation) {
        var httpError = this.getErrorMessageFromOperation(operation);
        if(httpError) {
            this.errormessages.push(httpError);
        }
    },

    /** Formats the error object returned by ``Ext.data.Operation.getError(). as
     * a string that can be displayed to users.
     * 
     * @return The formatted string.
     * */
    getErrorMessageFromOperation: function(operation) {
        var error = operation.getError();
        if(error === undefined) {
            return null;
        }
        var message;
        if(error.status === 0) {
            message = 'Could not connect to server.';
        } else {
            message = Ext.String.format('{0}: {1}', error.status, error.statusText);
        }
        return message;
    }
});
