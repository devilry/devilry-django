Ext.define('devilry_student.controller.AddDelivery', {
    extend: 'Ext.app.Controller',

    requires: [
        'Ext.window.MessageBox'
    ],

    views: [
        'add_delivery.AddDeliveryPanel'
    ],

    refs: [{
        ref: 'addDeliveryPanel',
        selector: 'viewport add_delivery'
    }, {
        ref: 'addDeliveryPanelForm',
        selector: 'viewport add_delivery form'
    }, {
        ref: 'metaBox',
        selector: 'viewport add_delivery #meta'
    }, {
        ref: 'helpBox',
        selector: 'viewport add_delivery #help'
    }, {
        ref: 'deliverButton',
        selector: 'viewport add_delivery #deliverbutton'
    }],

    init: function() {
        this.control({
            'viewport add_delivery': {
                render: this._onRender
            },
            'viewport add_delivery fileuploadfield': {
                change: this._onChooseFile
            },
            'viewport add_delivery #cancelbutton': {
                click: this._onCancel
            },
            'viewport add_delivery #deliverbutton': {
                click: this._onDeliver
            }
        });
    },

    _onRender: function() {
        this.groupInfoRecord = this.getAddDeliveryPanel().groupInfoRecord;
        this.uploadedfiles = [];
    },

    _onChooseFile: function() {
        this._submitForm();
    },

    _onCancel: function() {
        console.log('cancel');
    },

    _onDeliver: function() {
        this._setFormValues({
            finish: 'true'
        });
        this._submitForm();
    },



    _setLoading: function(message) {
        this.getAddDeliveryPanel().setLoading(message);
    },

    _setFormValues: function(values) {
        var form = this.getAddDeliveryPanelForm().getForm();
        form.setValues(values);
    },

    _submitForm: function() {
        var form = this.getAddDeliveryPanelForm().getForm();
        var url = Ext.String.format(
            '{0}/devilry_student/rest/add-delivery/{1}?format=json',
            DevilrySettings.DEVILRY_URLPATH_PREFIX, this.groupInfoRecord.get('id')
        );
        if(form.isValid()){
            this._setLoading(gettext('Uploading your file ...'));
            form.submit({
                url: url,
                scope: this,
                success: this._onSubmitFormSuccess,
                failure: this._onSubmitFormFailure
            });
        }
    },

    _onSubmitFormSuccess: function(form, action) {
        this._setLoading(false);
        var result = action.result;
        this._setFormValues({
            delivery_id: result.delivery_id,
            file_to_add: ''
        });
        if(result.added_filename) {
            this.uploadedfiles.push({
                filename: result.added_filename
            });
        }
        this._updateMeta();
        this._updateHelp(result);
        this.getDeliverButton().enable();
    },

    _onSubmitFormFailure: function(form, action) {
        this._setLoading(false);
        var result = action.result;
        Ext.MessageBox.show({
            title: gettext('Error'),
            msg: result.detail,
            icon: Ext.MessageBox.ERROR,
            buttons: Ext.MessageBox.OK
        });
    },


    _updateMeta: function() {
        this.getMetaBox().update({
            uploadedfiles: this.uploadedfiles
        });
    },

    _updateHelp: function(result) {
        this.getHelpBox().update({
            added_filename: result.added_filename,
            filenameCount: this.uploadedfiles.length,
            delivery_term: gettext('delivery')
        });
    }
});
