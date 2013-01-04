Ext.define('devilry_qualifiesforexam.controller.QualifiesForExamFrontpageController', {
    extend: 'Ext.app.Controller',

    views: [
        'QualifiesForExamFrontpage'
    ],

//    stores: [
//        'Plugins'
//    ],

//    refs: [{
//        ref: 'allWhereIsAdminList',
//        selector: 'allactivewhereisadminlist'
//    }],

    init: function() {
        this.control({
            'viewport frontpage': {
                render: this._onRender
            }
        });
//        this.mon(this.getPluginsStore().proxy, {
//            scope: this,
//            exception: this._onProxyError
//        });
    },

    _onRender: function() {
        console.log('render');
//        this.getPluginsStore().load({
//            scope: this,
//            callback: function(records, op) {
//                if(op.success) {
//                    this._onLoadSuccess(records);
//                } else {
//                    //NOTE: Errors are handled in _onProxyError
//                }
//            }
//        });
    },


    _onLoadSuccess: function(records) {
        console.log('success');
    },

    _onProxyError: function(proxy, response, operation) {
//        this.handleProxyErrorNoForm(this.application.getAlertmessagelist(),
//            response, operation);
        console.log('ERROR', response, operation);
    }
});

