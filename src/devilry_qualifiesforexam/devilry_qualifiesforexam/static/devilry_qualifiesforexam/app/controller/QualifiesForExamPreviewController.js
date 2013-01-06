Ext.define('devilry_qualifiesforexam.controller.QualifiesForExamPreviewController', {
    extend: 'Ext.app.Controller',

    views: [
        'preview.QualifiesForExamPreview'
    ],

//    models: [
//        'Preview'
//    ],

    requires: [
        'devilry_extjsextras.DjangoRestframeworkProxyErrorHandler',
        'devilry_extjsextras.HtmlErrorDialog'
    ],


    refs: [{
        ref: 'preview',
        selector: 'preview'
    }],

    init: function() {
        this.control({
            'viewport preview': {
                render: this._onRender
            }
        });
//        this.mon(this.getPluginsStore().proxy, {
//            scope: this,
//            exception: this._onProxyError
//        });
    },

    _onRender: function() {
        console.log('Render preview');
        var periodid = this.getPreview().periodid;
        var pluginsessionid = this.getPreview().pluginsessionid;
//        this.getPreviewModel().load({
//            scope: this,
//            callback: function(records, op) {
//                if(op.success) {
//                    this._onLoadSuccess(records);
//                }
//                NOTE: Errors are handled in _onProxyError
//            }
//        });
    },


    _onLoadSuccess: function(records) {
        // NOTE: This is not really needed since the view is loaded when the store is loaded, but it is nice to have for debugging.
    },

    _onProxyError: function(proxy, response, operation) {
        var errorhandler = Ext.create('devilry_extjsextras.DjangoRestframeworkProxyErrorHandler');
        errorhandler.addErrors(response, operation);
        this.application.getAlertmessagelist().addMany(errorhandler.errormessages, 'error', true);
    }
});

