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
    }],

    init: function() {
        this.control({
            'viewport add_delivery': {
                render: this._onRender
            },
            'viewport add_delivery fileuploadfield': {
                change: this._onChooseFile
            }
        });
    },

    _onRender: function() {
        this.groupInfoRecord = this.getAddDeliveryPanel().groupInfoRecord;
    },

    _onChooseFile: function() {
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
        console.log('success', action);
        var result = action.result;
        this._setFormValues({
            delivery_id: result.delivery_id
        });
    },

    _onSubmitFormFailure: function(form, action) {
        this._setLoading(false);
        console.log('failure', action);
        var result = action.result;
        Ext.MessageBox.show({
            title: gettext('Error'),
            msg: result.detail,
            icon: Ext.MessageBox.ERROR,
            buttons: Ext.MessageBox.OK
        });
    }
});
