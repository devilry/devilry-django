/**
 * Simplifies djangorestframework proxy error handling.
 */
Ext.define('devilry_subjectadmin.utils.DjangoRestframeworkProxyErrorMixin', {
    requires: [
        'devilry_extjsextras.DjangoRestframeworkProxyErrorHandler',
        'devilry_extjsextras.form.ErrorUtils',
        'devilry_extjsextras.HtmlErrorDialog'
    ],

    handleProxyError: function(alertmessagelist, formpanel, response, operation) {
        var errorhandler = Ext.create('devilry_extjsextras.DjangoRestframeworkProxyErrorHandler');
        errorhandler.addErrors(response, operation);
        alertmessagelist.addMany(errorhandler.errormessages, 'error', true);
        if(typeof formpanel !== 'undefined') {
            devilry_extjsextras.form.ErrorUtils.addFieldErrorsToAlertMessageList(formpanel,
                errorhandler.fielderrors, alertmessagelist);
            devilry_extjsextras.form.ErrorUtils.markFieldErrorsAsInvalid(formpanel,
                errorhandler.fielderrors);
        }
    },

    handleProxyErrorNoForm: function(alertmessagelist, response, operation) {
        this.handleProxyError(alertmessagelist, undefined, response, operation);
    },

    handleProxyUsingHtmlErrorDialog: function(response, operation) {
        var errorhandler = Ext.create('devilry_extjsextras.DjangoRestframeworkProxyErrorHandler');
        errorhandler.addErrors(response, operation);
        Ext.widget('htmlerrordialog', {
            bodyHtml: errorhandler.asHtmlList()
        }).show();
    }
});
