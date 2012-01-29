Ext.define('subjectadmin.controller.CreateNewAssignment', {
    extend: 'Ext.app.Controller',

    views: [
        'createnewassignment.Form',
        'createnewassignment.CreateNewAssignment'
    ],

    stores: [
        'ActiveAssignments'
    ],
    models: [
        'Assignment'
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
        this.control({
            'viewport createnewassignmentform': {
                render: this._onRenderForm,
            },
            'viewport createnewassignmentform textfield[name=long_name]': {
                render: this._onRenderLongName,
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
    },

    _setInitialValues: function() {
        this.getForm().getForm().setValues({
            long_name: 'The first assignment',
            short_name: 'firstassignment'
        })
    },

    _onSubmit: function() {
        if(this.getForm().getForm().isValid()) {
            this._save();
        }
    },

    _getFormValues: function() {
        return this.getForm().getForm().getFieldValues();
    },

    _save: function() {
        this.getAlertMessageList().removeAll();
        var values = this._getFormValues();
        var periodId = this.getCreateNewAssignment().periodId;
        values.parentnode = periodId;

        var AssignmentModel = this.getAssignmentModel();
        var assignment = new AssignmentModel(values);
        this._mask();
        assignment.save({
            scope: this,
            success: this._onSuccessfulSave,
            failure: this._onFailedSave
        });
    },

    _onSuccessfulSave: function() {
        this._unmask();
        console.log('success');
    },

    _onFailedSave: function(record, operation) {
        this._unmask();

        console.log(operation);
        if(operation.responseData && operation.responseData.items.errormessages) {
            var errors = operation.responseData.items;
            this._addGlobalErrorMessages(errors.errormessages);
            this._addFieldErrorMessages(errors.fielderrors);
        } else {
            var error = operation.getError();
            var message;
            if(error.status === 0) {
                message = dtranslate('themebase.lostserverconnection');
            } else {
                message = Ext.String.format('{0}: {1}', error.status, error.statusText);
            }
            this.getAlertMessageList().add({
                message: message,
                type: 'error'
            });
        }
    },

    _addGlobalErrorMessages: function(errormessages) {
        Ext.Array.each(errormessages, function(message) {
            this.getAlertMessageList().add({
                message: message,
                type: 'error'
            });
        }, this);
    },

    _addFieldErrorMessages: function(fielderrors) {
        Ext.Object.each(fielderrors, function(fieldname, fielderrors) {
            var fieldComponentQuery = Ext.String.format('field[name={0}]', fieldname);
            var match = this.getForm().query(fieldComponentQuery);
            if(match.length > 0) {
                var field = match[0];
                field.markInvalid(fielderrors);
            }
        }, this);
    },

    _mask: function() {
        this.getForm().getEl().mask(dtranslate('themebase.saving'))
    },
    _unmask: function() {
        this.getForm().getEl().unmask();
    }
});
