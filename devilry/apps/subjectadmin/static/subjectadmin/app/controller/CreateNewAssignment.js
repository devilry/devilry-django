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
    // Page one
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

    // Page two
    }, {
        ref: 'createNewAssignmentForm',
        selector: 'createnewassignmentform'
    }, {
        ref: 'createNewAssignment',
        selector: 'createnewassignment'
    }, {
        ref: 'pageTwoAlertMessageList',
        selector: 'createnewassignment alertmessagelist'
    }, {
        ref: 'metainfo',
        selector: 'createnewassignmentform #metainfo'
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
            // Page one
            'viewport chooseperiod form': {
                afterrender: this._onRenderPageOneForm
            },
            'viewport chooseperiod activeperiodslist': {
                afterrender: this._onRenderActivePeriodlist
            },
            'viewport chooseperiod nextbutton': {
                click: this._onNextFromPageOne
            },

            // Page two
            'viewport createnewassignmentform': {
                render: this._onRenderCreateNewAssignmentForm,
            },
            'viewport createnewassignmentform textfield[name=long_name]': {
                render: this._onRenderLongName
            },
            'viewport createnewassignmentform createbutton': {
                click: this._onCreate,
            },
            'viewport createnewassignmentform combobox[name=delivery_types]': {
                select: this._onDeliveryTypesSelect
            },
            'viewport createnewassignmentform checkboxfield[name=add_all_relatedstudents]': {
                change: this._onAddRelatedStudentChange
            }
        });
    },

    _loadPeriodsIfNotLoaded: function(callback) {
        if(this.getActivePeriodsStore().getCount() > 0) {
            Ext.callback(callback, this);
        } else {
            this.getActivePeriodsStore().load({
                scope: this,
                callback: callback
            });
        }
    },

    //////////////////////////////////////////////
    //
    // Page one
    //
    //////////////////////////////////////////////

    _onRenderPageOneForm: function() {
        this.getPageOneForm().keyNav = Ext.create('Ext.util.KeyNav', this.getPageOneForm().el, {
            enter: this._onNextFromPageOne,
            scope: this
        });
    },

    _onRenderActivePeriodlist: function() {
        this.getActivePeriodsList().getEl().mask(dtranslate('themebase.loading'));
        this._loadPeriodsIfNotLoaded(this._addItemsToActivePeriodList);
    },

    _handleNoActivePeriods: function() {
        this.getNextFromPageOneButton().disable();
        this.getPageOneAlertMessageList().add({
            message: dtranslate('subjectadmin.assignment.error.no_active_periods'),
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
            this.getActivePeriodsList().query('radio')[0].focus();
        }, 50, this);
    },

    _onNextFromPageOne: function() {
        var formvalues = this.getPageOneForm().getForm().getFieldValues();
        var delivery_types = formvalues.delivery_types;
        var activeperiod = formvalues.activeperiod;
        var nexturlformat = '/@@create-new-assignment/{0},{1}';
        var nexturl = Ext.String.format(nexturlformat, activeperiod, delivery_types);
        this.application.route.navigate(nexturl);
    },




    //////////////////////////////////////////////
    //
    // Page two
    //
    //////////////////////////////////////////////

    _onRenderLongName: function(field) {
        field.focus();
    },

    _onRenderCreateNewAssignmentForm: function() {
        this.period_id = this.getCreateNewAssignment().period_id;
        this.delivery_types = this.getCreateNewAssignment().delivery_types;
        this._loadPeriodsIfNotLoaded(this._showPageOneMetadata);
        this.getCreateNewAssignmentForm().keyNav = Ext.create('Ext.util.KeyNav', this.getCreateNewAssignmentForm().el, {
            enter: this._onCreate,
            scope: this
        });
        this._setInitialValues();

        this.getCreateNewAssignmentForm().mon(this.getCreateNewAssignmentModel().proxy, {
            scope:this,
            exception: this._onProxyError
        });
    },

    _handleNotActivePeriod: function() {
        var message = Ext.create('Ext.XTemplate',
            dtranslate('subjectadmin.assignment.error.not_active_period')
        ).apply({period_id: this.period_id});
        this.getPageTwoAlertMessageList().add({
            message: message,
            type: 'error'
        });
    },

    _showPageOneMetadata: function() {
        var periodRecord = this.getActivePeriodsStore().findRecord('id', this.period_id);
        if(periodRecord) {
            var type;
            if(this.delivery_types == 0) {
                type = dtranslate('subjectadmin.assignment.delivery_types.electronic');
            } else {
                type = dtranslate('subjectadmin.assignment.delivery_types.nonelectronic');
            }
            var metatext = Ext.create('Ext.XTemplate',
                dtranslate('subjectadmin.createnewassignment.metatext')
            ).apply({
                period: periodRecord.get('parentnode__short_name') + '.' + periodRecord.get('short_name'),
                type: type
            });
            this.getMetainfo().update(metatext);
        } else {
            this._handleNotActivePeriod();
        }
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
        //this.getCreateNewAssignmentForm().getForm().setValues({
            //long_name: 'A',
            //short_name: 'a'
        //})
    //},

    _onCreate: function() {
        if(this.getCreateNewAssignmentForm().getForm().isValid()) {
            this._save();
        }
    },

    _getFormValues: function() {
        var values = this.getCreateNewAssignmentForm().getForm().getFieldValues();
        return values;
    },

    _save: function() {
        this.getPageTwoAlertMessageList().removeAll();
        var values = this._getFormValues();
        values.period_id = this.period_id;
        values.delivery_types = this.delivery_types;

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
        this.getPageTwoAlertMessageList().addMany(errorhandler.errormessages, 'error');
        themebase.form.ErrorUtils.addFieldErrorsToAlertMessageList(
            this.getCreateNewAssignmentForm(), errorhandler.fielderrors, this.getPageTwoAlertMessageList()
        );
        themebase.form.ErrorUtils.markFieldErrorsAsInvalid(
            this.getCreateNewAssignmentForm(), errorhandler.fielderrors
        );
    },

    _mask: function() {
        this.getCreateNewAssignmentForm().getEl().mask(dtranslate('themebase.saving'))
    },
    _unmask: function() {
        this.getCreateNewAssignmentForm().getEl().unmask();
    }
});
