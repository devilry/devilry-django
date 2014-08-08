/**
 * Requirements:
 *
 *      - Have an alertmessagelist registered as the ``globalAlertmessagelist`` ref.
 */
Ext.define('devilry_subjectadmin.utils.DjangoRestframeworkLoadFailureMixin', {
    requires: ['devilry_extjsextras.DjangoRestframeworkProxyErrorHandler'],

    onLoadFailure: function(operation) {
        var error = Ext.create('devilry_extjsextras.DjangoRestframeworkProxyErrorHandler', operation);
        error.addErrors(null, operation);
        this.getGlobalAlertmessagelist().addMany(error.errormessages, 'error', true);
    }
});
