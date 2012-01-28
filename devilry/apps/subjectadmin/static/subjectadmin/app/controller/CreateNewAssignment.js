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
        console.log('error', record, operation);
    },

    _mask: function() {
        this.getForm().getEl().mask(dtranslate('themebase.saving'))
    },
    _unmask: function() {
        this.getForm().getEl().unmask();
    }
});
