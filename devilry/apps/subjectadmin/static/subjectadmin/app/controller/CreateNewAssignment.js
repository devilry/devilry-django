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
        ref: 'pageOneForm',
        selector: 'chooseperiod form'
    }, {
        ref: 'pageOneAlertMessageList',
        selector: 'chooseperiod alertmessagelist'
    }, {
        ref: 'form',
        selector: 'createnewassignmentform'
    }, {
        ref: 'createNewAssignment',
        selector: 'createnewassignment'
    }, {
        ref: 'alertMessageList',
        selector: 'createnewassignment alertmessagelist'
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
                afterrender: this._onRenderActivePeriodlist
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
        var delivery_types = this.getCreateNewAssignment().delivery_types;
        values.period_id = periodId;
        values.delivery_types = delivery_types;

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
        this.getActivePeriodsList().getEl().mask(dtranslate('themebase.loading'));
        if(this.getActivePeriodsStore().getCount() > 0) {
            this._addItemsToActivePeriodList();
        } else {
            this.getActivePeriodsStore().load({
                scope: this,
                callback: this._addItemsToActivePeriodList
            });
        }
    },

    _handleNoActivePeriods: function() {
        this.getNextFromPageOneButton().disable();
        this.getPageOneAlertMessageList().add({
            message: dtranslate('subjectadmin.assignment.noactiveperiods'),
            type: 'error'
        });
    },

    _addItemsToActivePeriodList: function() {
        this.getActivePeriodsList().removeAll();
        if(this.getActivePeriodsStore().getCount() === 0) {
            this.getActivePeriodsList().getEl().unmask();
            this._handleNoActivePeriods();
        }
        Ext.defer(function() {
            this.getActivePeriodsStore().each(function(periodRecord, index) {
                this.getActivePeriodsList().addPeriod(periodRecord, index===0);
            }, this);
            this.getActivePeriodsList().getEl().unmask();
        }, 50, this);
    },

    _onNextFromPageOne: function() {
        var formvalues = this.getPageOneForm().getForm().getFieldValues();
        var delivery_types = formvalues.delivery_types;
        var activeperiod = formvalues.activeperiod;
        var nexturlformat = '/@@create-new-assignment/{0},{1}';
        var nexturl = Ext.String.format(nexturlformat, activeperiod, delivery_types);
        this.application.route.navigate(nexturl);
    }
});
