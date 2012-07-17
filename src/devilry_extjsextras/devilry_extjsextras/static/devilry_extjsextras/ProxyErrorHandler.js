/**
 * Base class for proxy error handling.
 */
Ext.define('devilry_extjsextras.ProxyErrorHandler', {
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

    _formatTpl: function(tpl, data) {
        return Ext.create('Ext.XTemplate', tpl).apply(data);
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
        var url = operation.request.url;
        if(error.status === 0) {
            message = this._formatTpl(gettext('Could not connect to server at URL "{url}".'), {
                url: url
            });
        } else {
            message = this._formatTpl('The server responded with error message "{status}: {statusText}" when we did a {method}-request to URL "{url}".', {
                status: error.status,
                statusText: error.statusText,
                method: operation.request.method,
                url: operation.request.url
            });
        }
        return message;
    },

    /**
     * Copy errormessages and fielderrors into a single array, and return the array.
     * Each item in the array is a string. Fielderrors are formatted as
     * ``"{fieldname}: {message}"``.
     */
    asArrayOfStrings: function() {
        var messages = Ext.clone(this.errormessages);
        Ext.Object.each(this.fielderrors, function(message, fieldname) {
            messages.push(Ext.String.format('{0}: {1}', fieldname, message));
        }, this);
        return messages;
    },

    /**
     * Uses #asArrayOfStrings to flatten the error messages, then put these
     * messages in a HTML unordered list.
     * */
    asHtmlList: function() {
        return Ext.create('Ext.XTemplate',
            '<ul>',
            '<tpl for="messages">',
                '<li>{.}</li>',
            '</tpl>',
            '</ul>'
        ).apply({
            messages: this.asArrayOfStrings()
        });
    }
});
