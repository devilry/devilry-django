/**
 * 
 */
Ext.define('themebase.ProxyErrorHandler', {
    constructor: function(operation) {
        this.errormessages = [];
        this.fielderrors = {};
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
            message = dtranslate('themebase.lostserverconnection');
        } else {
            message = Ext.String.format('{0}: {1}', error.status, error.statusText);
        }
        return message;
    }
});
