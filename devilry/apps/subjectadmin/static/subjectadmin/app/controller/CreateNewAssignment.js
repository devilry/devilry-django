Ext.define('subjectadmin.controller.CreateNewAssignment', {
    extend: 'Ext.app.Controller',

    requires: [
        'themebase.form.ErrorUtils'
    ],
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
    //}, {
        //ref: 'shortNameField',
        //selector: 'textfield[name=short_name]'
    //}, {
        //ref: 'longNameField',
        //selector: 'textfield[name=long_name]'
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
    },

    _setInitialValues: Ext.emptyFn,
    //_setInitialValues: function() {
        //this.getForm().getForm().setValues({
            //long_name: 'The first assignment',
            //short_name: 'firstassignment'
        //})
    //},

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

    //_createShortNameFromLongname: function(longname) {
        //var shortname = longname.toLowerCase();
        //shortname = shortname.replace(/\s+/g, '-').replace(/[^a-z0-9_-]/g, '');
        ////if(shortname.length > 20) {
            ////var prefix = shortname.substring(0, 10);
            ////var suffix = shortname.substring(shortname.length - 9);
            ////shortname = prefix + '-' + suffix;
        ////}
        //return shortname;
    //},

    //_onLongNameChange: function() {
        //var shortname = this.getShortNameField().getValue();
        //var longname = this.getLongNameField().getValue();
        //if(this._shouldAutosetShortname()) {
            //var shortname = this._createShortNameFromLongname(longname);
            //console.log(shortname);
            //if(shortname.length <= 20) {
                //this.getShortNameField().setValue(shortname);
            //}
        //}
    //},

    _onSuccessfulSave: function() {
        this._unmask();
        console.log('success');
    },

    _onFailedSave: function(record, operation) {
        this._unmask();
        themebase.form.ErrorUtils.handleRestErrorsInForm(operation, this.getForm(), this.getAlertMessageList());
    },

    _mask: function() {
        this.getForm().getEl().mask(dtranslate('themebase.saving'))
    },
    _unmask: function() {
        this.getForm().getEl().unmask();
    }
});
