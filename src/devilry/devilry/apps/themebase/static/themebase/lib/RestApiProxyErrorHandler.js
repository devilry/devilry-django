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

    _translate: function(i18ndata) {
        var i18nkey = i18ndata[0];
        var i18nparameters = i18ndata[1];
        var message = dtranslate(i18nkey);
        console.log(message, i18nparameters);
        if(i18nparameters) {
            message = Ext.create('Ext.XTemplate', message).apply(i18nparameters);
        }
        return message;
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
            Ext.Array.each(responseData.i18nErrormessages, function(i18ndata) {
                this.errormessages.push(this._translate(i18ndata));
            }, this);
            Ext.Object.each(responseData.i18nFielderrors, function(fieldname, i18ndatalist) {
                var messages =  [];
                Ext.Array.each(i18ndatalist, function(i18ndata) {
                    messages.push(this._translate(i18ndata));
                }, this);
                this.fielderrors[fieldname] = messages;
            }, this);
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
