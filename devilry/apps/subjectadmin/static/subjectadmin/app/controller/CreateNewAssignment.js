Ext.define('subjectadmin.controller.CreateNewAssignment', {
    extend: 'Ext.app.Controller',

    requires: [
        'themebase.NextButton',
        'themebase.form.ErrorUtils',
        'themebase.RestApiProxyErrorHandler'
    ],
    views: [
        'ActivePeriodsList',
        'createnewassignment.Form',
        'createnewassignment.SuccessPanel',
        'createnewassignment.CreateNewAssignment'
    ],

    models: [
        'CreateNewAssignment'
    ],

    stores: [
        'ActivePeriods'
    ],

    refs: [{
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
        ref: 'deliveryTypesRadioGroup',
        selector: 'createnewassignmentform #deliveryTypesRadioGroup'
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
            'viewport createnewassignmentform radiogroup radio': {
                change: this._onDeliveryTypesSelect
            },
            'viewport createnewassignmentform checkboxfield[name=add_all_relatedstudents]': {
                change: this._onAddRelatedStudentChange
            },
            'viewport fieldset': {
                afterlayout: function() {
                    // NOTE: When the fieldset is expanded, we get horizontal scrolling without this workaround
                    this.getCreateNewAssignmentForm().doLayout();
                }
            },

            // Success page
            'viewport createnewassignment-successpanel': {
                render: this._onRenderSuccesspanel
            },
        });
    },

    _loadPeriodsIfNotLoaded: function(callback) {
        if(this.getActivePeriodsStore().getCount() > 0) {
            Ext.callback(callback, this);
        } else {
            this.getActivePeriodsStore().loadActivePeriods({
                scope: this,
                callback: callback
            });
        }
    },

    //_selectAppropriateDeliverytypes: function() {
        //var radioButtons = this.getDeliveryTypesRadioGroup().query('radio');
        //var index = 0;
        //if(this.successPanelSetupConfig) {
            //index = this.successPanelSetupConfig.delivery_types;
        //}
        //radioButtons[index].setValue(true);
    //},


    _onRenderLongName: function(field) {
        field.focus();
    },

    _onRenderCreateNewAssignmentForm: function() {
        this.period_id = this.getCreateNewAssignment().period_id;
        this._loadPeriodsIfNotLoaded(this._showMetadata);
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

    _showMetadata: function() {
        var periodRecord = this.getActivePeriodsStore().findRecord('id', this.period_id);
        if(periodRecord) {
            var metatext = Ext.create('Ext.XTemplate',
                dtranslate('subjectadmin.createnewassignment.metatext')
            ).apply({
                period: periodRecord.get('parentnode__short_name') + '.' + periodRecord.get('short_name')
            });
            this.getMetainfo().update(metatext);
            this.periodRecord = periodRecord;
        } else {
            this._handleNotActivePeriod();
        }
    },

    _onDeliveryTypesSelect: function(radio, records) {
        var is_electronic = radio.getGroupValue() === 0;
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
        //values.delivery_types = this.delivery_types;

        var CreateNewAssignmentModel = this.getCreateNewAssignmentModel();
        var assignment = new CreateNewAssignmentModel(values);
        this._mask();
        assignment.save({
            scope: this,
            success: this._onSuccessfulSave
        });
    },

    _onSuccessfulSave: function() {
        this._unmask();
        this.successPanelSetupConfig = {
            period_id: this.period_id,
            delivery_types: this.delivery_types,
            period_short_name: this.periodRecord.get('short_name'),
            subject_short_name: this.periodRecord.get('parentnode__short_name'),
            short_name: this._getFormValues().short_name
        };
        this.application.route.navigate('/@@create-new-assignment/@@success');
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
    },



    //////////////////////////////////////////////
    //
    // Success page
    //
    //////////////////////////////////////////////
    _onRenderSuccesspanel: function(successpanel) {
        if(!this.successPanelSetupConfig) {
            Ext.MessageBox.alert('Error', 'This page is only available after creating a new assignment.');
        } else {
            successpanel.setup(this.successPanelSetupConfig);
        }
    }
});
