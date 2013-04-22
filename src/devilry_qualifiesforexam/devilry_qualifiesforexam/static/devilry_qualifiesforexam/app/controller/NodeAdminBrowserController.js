Ext.define('devilry_qualifiesforexam.controller.NodeAdminBrowserController', {
    extend: 'Ext.app.Controller',

    //views: [
        //'preview.QualifiesForExamPreview'
    //],

    //stores: [
        //'RelatedStudents'
    //],

    //models: [
        //'Preview'
    //],

    //requires: [
    //],


    refs: [{
        ref: 'preview',
        selector: 'preview'
    }, {
        ref: 'previewGrid',
        selector: 'preview previewgrid'
    }],

    init: function() {
        //this.control({
            //'viewport preview previewgrid': {
                //render: this._onRender
            //},
            //'viewport preview #saveButton': {
                //click: this._onSave
            //},
            //'viewport preview #backButton': {
                //click: this._onBack
            //}
        //});
        //this.mon(this.getPreviewModel().proxy, {
            //scope: this,
            //exception: this._onProxyError
        //});
    },

    _onRender: function() {
        //this.getPreview().setLoading();
        //this.periodid = this.getPreview().periodid;
        //this.pluginid = this.getPreview().pluginid;
        //this.pluginsessionid = this.getPreview().pluginsessionid;
        //this.application.setTitle(gettext('Preview and confirm'));
        //this.loadPeriod(this.periodid);
    },


    _onProxyError: function(proxy, response, operation) {
        //this.getPreview().setLoading(false);
        //var errorhandler = Ext.create('devilry_extjsextras.DjangoRestframeworkProxyErrorHandler');
        //errorhandler.addErrors(response, operation);
        //this.application.getAlertmessagelist().addMany(errorhandler.errormessages, 'error', true);
    }
});
