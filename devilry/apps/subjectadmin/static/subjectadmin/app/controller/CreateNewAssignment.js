Ext.define('subjectadmin.controller.CreateNewAssignment', {
    extend: 'Ext.app.Controller',

    requires: [
        'themebase.NextButton',
        'themebase.form.ErrorUtils',
        'themebase.RestApiProxyErrorHandler'
    ],
    views: [
        'ActivePeriodsList',
        'createnewassignment.ChoosePeriod',
        'createnewassignment.Form',
        'createnewassignment.CreateNewAssignment'
    ],

    models: [
        'CreateNewAssignment'
    ],

    stores: [
        'ActivePeriods'
    ],

    refs: [{
        ref: 'nextFromPageOneButton',
        selector: 'chooseperiod nextbutton'
    }, {
        ref: 'choosePeriod',
        selector: 'chooseperiod'
    }, {
        ref: 'activePeriodsList',
        selector: 'chooseperiod activeperiodslist'
    }, {
        ref: 'form',
        selector: 'createnewassignmentform'
    }, {
        ref: 'createNewAssignment',
        selector: 'createnewassignment'
    }, {
        ref: 'alertMessageList',
        selector: 'alertmessagelist'
    }, {
        ref: 'firstDeadlineField',
        selector: 'createnewassignmentform themebase-datetimefield[name=first_deadline]'
    }, {
        ref: 'firstDeadlineHelp',
        selector: 'createnewassignmentform #first_deadline-help'
    }, {
        ref: 'autoSetupExaminersField',
        selector: 'createnewassignmentform checkboxfield[name=autosetup_examiners]'
    }, {
        ref: 'autoSetupExaminersHelp',
        selector: 'createnewassignmentform #autosetup_examiners-help'
    }],

    init: function() {
        this.getActivePeriodsStore().load();
        this.control({
            'viewport createnewassignmentform': {
                render: this._onRenderForm,
            },
            'viewport createnewassignmentform textfield[name=long_name]': {
                render: this._onRenderLongName
            },
            'viewport createnewassignmentform createbutton': {
                click: this._onSubmit,
            },
            'viewport createnewassignmentform combobox[name=delivery_types]': {
                select: this._onDeliveryTypesSelect
            },
            'viewport createnewassignmentform checkboxfield[name=add_all_relatedstudents]': {
                change: this._onAddRelatedStudentChange
            },
            'viewport chooseperiod activeperiodslist': {
                render: this._onRenderActivePeriodlist,
                select: this._onSelectPeriod,
                deselect: this._onDeSelectPeriod
            },
            'viewport chooseperiod nextbutton': {
                click: this._onNextFromPageOne
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

    _onDeliveryTypesSelect: function(combo, records) {
        var record = records[0];
        var is_electronic = record.get('value') === 0;
        if(is_electronic) {
            this.getFirstDeadlineField().show();
            this.getFirstDeadlineHelp().show();
        } else {
            this.getFirstDeadlineField().hide();
            this.getFirstDeadlineHelp().hide();
        }
    },

    _onAddRelatedStudentChange: function(field, addAllRelatedStudents) {
        if(addAllRelatedStudents) {
            this.getAutoSetupExaminersField().show();
            this.getAutoSetupExaminersHelp().show();
        } else {
            this.getAutoSetupExaminersField().hide();
            this.getAutoSetupExaminersHelp().hide();
        }
    },

    _setInitialValues: Ext.emptyFn,

    //_setInitialValues: function() {
        //this.getForm().getForm().setValues({
            //long_name: 'A',
            //short_name: 'a'
        //})
    //},

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

        var CreateNewAssignmentModel = this.getCreateNewAssignmentModel();
        var assignment = new CreateNewAssignmentModel(values);
        this._mask();
        assignment.save({
            scope: this,
            success: this._onSuccessfulSave
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
    },


    _onRenderActivePeriodlist: function() {
        this.getNextFromPageOneButton().disable();
    },

    _onDeSelectPeriod: function() {
        this.getNextFromPageOneButton().disable();
    },
    _onSelectPeriod: function() {
        this.getNextFromPageOneButton().enable();
    },

    _onNextFromPageOne: function() {
        var nexturlformat = '/@@create-new-assignment/{0}';
        var periodid = this.getActivePeriodsList().getSelectionModel().getLastSelected().get('id');
        var nexturl = Ext.String.format(nexturlformat, periodid);
        this.application.route.navigate(nexturl);
    }
});
