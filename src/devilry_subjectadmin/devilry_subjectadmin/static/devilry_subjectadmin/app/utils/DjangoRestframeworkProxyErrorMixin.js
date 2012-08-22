/**
 * Simplifies djangorestframework proxy error handling.
 */
Ext.define('devilry_subjectadmin.utils.DjangoRestframeworkProxyErrorMixin', {
    requires: [
        'devilry_extjsextras.DjangoRestframeworkProxyErrorHandler',
        'devilry_extjsextras.form.ErrorUtils'
    ],

    handleProxyError: function(alertmessagelist, formpanel, response, operation) {
        var errorhandler = Ext.create('devilry_extjsextras.DjangoRestframeworkProxyErrorHandler');
        errorhandler.addErrors(response, operation);
        alertmessagelist.addMany(errorhandler.errormessages, 'error');
        if(typeof formpanel !== 'undefined') {
            devilry_extjsextras.form.ErrorUtils.addFieldErrorsToAlertMessageList(formpanel,
                errorhandler.fielderrors, alertmessagelist);
            devilry_extjsextras.form.ErrorUtils.markFieldErrorsAsInvalid(formpanel,
                errorhandler.fielderrors);
        }
    },

    handleProxyErrorNoForm: function(alertmessagelist, response, operation) {
        this.handleProxyError(alertmessagelist, undefined, response, operation);
    }
});
