Ext.define('subjectadmin.controller.CreateNewAssignment', {
    extend: 'Ext.app.Controller',

    requires: [
        'themebase.form.ErrorUtils',
        'themebase.RestApiProxyErrorHandler'
    ],
    views: [
        'createnewassignment.Form',
        'createnewassignment.CreateNewAssignment'
    ],

    models: [
        'CreateNewAssignment'
    ],

    refs: [{
        ref: 'form',
        selector: 'createnewassignmentform'
    }, {
        ref: 'createNewAssignment',
        selector: 'createnewassignment'
    }, {
        ref: 'alertMessageList',
        selector: 'alertmessagelist'
    }],

    init: function() {
        this.shortNameManuallyChanged = false;
        this.control({
            'viewport createnewassignmentform': {
                render: this._onRenderForm,
            },
            'viewport createnewassignmentform textfield[name=long_name]': {
                render: this._onRenderLongName
            },
            'viewport createnewassignmentform createbutton': {
                click: this._onSubmit,
            }
        });
    },

    _onRenderLongName: function(field) {
        field.focus();
    },

    _onRenderForm: function() {
        this.getForm().keyNav = Ext.create('Ext.util.KeyNav', this.getForm().el, {
            enter: this._onSubmit,
            scope: this
        });
        this._setInitialValues();

        this.getForm().mon(this.getCreateNewAssignmentModel().proxy, {
            scope:this,
            exception: this._onProxyError
        });
    },

    _setInitialValues: Ext.emptyFn,

    _setInitialValues: function() {
        this.getForm().getForm().setValues({
            long_name: 'A',
            short_name: 'A'
        })
    },

    _onSubmit: function() {
        if(this.getForm().getForm().isValid()) {
            this._save();
        }
    },

    _getFormValues: function() {
        var values = this.getForm().getForm().getFieldValues();
        return values;
    },

    _save: function() {
        this.getAlertMessageList().removeAll();
        var values = this._getFormValues();
        var periodId = this.getCreateNewAssignment().periodId;
        values.period_id = periodId;
        //console.log(values);

        var CreateNewAssignmentModel = this.getCreateNewAssignmentModel();
        var assignment = new CreateNewAssignmentModel(values);
        this._mask();
        assignment.save({
            scope: this,
            success: this._onSuccessfulSave
            //failure: this._onFailedSave
        });
    },

    _onSuccessfulSave: function(a, b, c) {
        this._unmask();
        console.log('success');
    },

    _onProxyError: function(proxy, response, operation) {
        this._unmask();
        var errorhandler = Ext.create('themebase.RestApiProxyErrorHandler');
        errorhandler.addErrors(response, operation);
        this.getAlertMessageList().addMany(errorhandler.errormessages, 'error');
        themebase.form.ErrorUtils.addFieldErrorsToAlertMessageList(
            this.getForm(), errorhandler.fielderrors, this.getAlertMessageList()
        );
        themebase.form.ErrorUtils.markFieldErrorsAsInvalid(
            this.getForm(), errorhandler.fielderrors
        );
    },

    _mask: function() {
        this.getForm().getEl().mask(dtranslate('themebase.saving'))
    },
    _unmask: function() {
        this.getForm().getEl().unmask();
    }
});
