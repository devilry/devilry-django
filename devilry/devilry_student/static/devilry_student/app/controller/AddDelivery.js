Ext.define('devilry_student.controller.AddDelivery', {
    extend: 'Ext.app.Controller',

    requires: [
        'Ext.window.MessageBox',
        'Ext.form.field.Checkbox'
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
    }, {
        ref: 'nativeFileUpload',
        selector: 'viewport add_delivery native_file_upload'
    }],

    init: function() {
        this.control({
            'viewport add_delivery': {
                render: this._onRender
            },
            'viewport add_delivery confirm_after_deadline checkbox': {
                change: this._onConfirmAfterDeadlineChange
            },
            'viewport add_delivery native_file_upload': {
                change: this._onNativeChooseFile
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


    _onNativeChooseFile: function(field) {
        if(!Ext.isEmpty(field.getValue())) {
            this._submitForm();
        }
    },

    _onCancel: function() {
        this.getAddDeliveryPanel().fireEvent('deliveryCancelled');
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
                method: 'post',
                params: {
                    respond_with_html_contenttype: true,
                    respond_with_200_status_on_error: Ext.isIE // NOTE: IE does not seem to handle HTTP status codes other than 200 (at least not 8 or 9). Since ExtJS checks the "success" attribute of the response, using 200 status codes works
                },
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
            this._updateMeta();
            this._updateHelp(result);
        }
        this._enableDeliveryIfValid();
        if(result.finished) {
            this._onFinished(result.delivery_id);
        }
    },

    _onConfirmAfterDeadlineChange: function(field, newValue) {
        this.afterDeadlineConfirmed = newValue;
        this._enableDeliveryIfValid();
    },

    _enableDeliveryIfValid: function() {
        if(this.uploadedfiles.length > 0) {
            if(this.groupInfoRecord.deadline_expired()) {
                if(this.afterDeadlineConfirmed) {
                    this.getDeliverButton().enable();
                    return;
                }
            } else {
                this.getDeliverButton().enable();
                return;
            }
        }
        this.getDeliverButton().disable();
    },

    _onSubmitFormFailure: function(form, action) {
        this._setLoading(false);
        this._setFormValues({
            file_to_add: '' // Reset file input field to make "Finish delivery" not use the file with error
        });
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
    },

    _onFinished: function(delivery_id) {
        this.getAddDeliveryPanel().fireEvent('deliveryFinished', delivery_id);
    }
});
