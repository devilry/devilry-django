Ext.define('devilry_qualifiesforexam.utils.CreateStatus', {
    singleton: true,
    requires: [
        'devilry_extjsextras.DjangoRestframeworkProxyErrorHandler'
    ],

    create: function (args, config) {
        var requestConfig = {
            url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_qualifiesforexam/rest/status/',
            method: 'POST',
            jsonData: args,
            extraParams: {
            format: 'json'
            }
        };
        Ext.apply(requestConfig, config);
        Ext.Ajax.request(requestConfig);
    },

    addErrorsToAlertmessagelist: function(response, alertmessagelist) {
        var errorhandler = Ext.create('devilry_extjsextras.DjangoRestframeworkProxyErrorHandler');
        errorhandler.addRestErrorsFromResponse(response);
        alertmessagelist.addMany(
            errorhandler.asArrayOfStrings(), 'error', true);
    }
});

