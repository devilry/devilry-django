Ext.define('devilry_subjectadmin.controller.CreateNewAssignment', {
    extend: 'Ext.app.Controller',
    mixins: {
        'basenodeBreadcrumbMixin': 'devilry_subjectadmin.utils.BasenodeBreadcrumbMixin',
        'onLoadFailure': 'devilry_subjectadmin.utils.DjangoRestframeworkLoadFailureMixin',
        'handleProxyError': 'devilry_subjectadmin.utils.DjangoRestframeworkProxyErrorMixin'
    },

    requires: [
        'Ext.Date',
        'devilry_extjsextras.NextButton',
        'devilry_extjsextras.form.ErrorUtils',
        'devilry_extjsextras.DjangoRestframeworkProxyErrorHandler'
    ],
    views: [
        'createnewassignment.Form',
        'createnewassignment.SuccessPanel',
        'createnewassignment.CreateNewAssignment'
    ],

    models: [
        'CreateNewAssignment',
        'Period'
    ],

    refs: [{
        ref: 'createNewAssignmentForm',
        selector: 'createnewassignmentform'
    }, {
        ref: 'createNewAssignment',
        selector: 'createnewassignment'
    }, {
        ref: 'globalAlertmessagelist',
        selector: 'createnewassignment alertmessagelist'
    }, {
        ref: 'metainfo',
        selector: 'createnewassignmentform #metainfo'
    }, {
        ref: 'deliveryTypesRadioGroup',
        selector: 'createnewassignmentform #deliveryTypesRadioGroup'
    }, {
        ref: 'firstDeadlineField',
        selector: 'createnewassignmentform devilry_extjsextras-datetimefield[name=first_deadline]'
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

            // Success page
            'viewport createnewassignment-successpanel': {
                render: this._onRenderSuccesspanel
            },
        });
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
        Ext.defer(function() {
            // NOTE: Using defer avoids that the text style remains
            // emptyText-gray (I assume it does no because render is fired
            // before the style is applied).
            field.focus();
        }, 100);
    },

    _onRenderCreateNewAssignmentForm: function() {
        this.getCreateNewAssignmentForm().keyNav = Ext.create('Ext.util.KeyNav', this.getCreateNewAssignmentForm().el, {
            enter: this._onCreate,
            scope: this
        });
        this._setInitialValues();

        this.getCreateNewAssignmentForm().mon(this.getCreateNewAssignmentModel().proxy, {
            scope: this,
            exception: this._onProxyError
        });
        this.period_id = this.getCreateNewAssignment().period_id;
        this._loadPeriod(this.period_id);
    },

    _loadPeriod: function(period_id) {
        this.getPeriodModel().load(period_id, {
            scope: this,
            callback: function(record, operation) {
                if(operation.success) {
                    this._onLoadPeriodSuccess(record);
                } else {
                    this._onLoadPeriodFailure(operation);
                }
            }
        });
    },
    _onLoadPeriodSuccess: function(record) {
        this.periodRecord = record;
        this.periodpath = this.getPathFromBreadcrumb(this.periodRecord);
        this._setMetadata();
    },
    _onLoadPeriodFailure: function(operation) {
        var message = Ext.create('Ext.XTemplate',
            gettext('Period {period_id} could not be loaded.')
        ).apply({period_id: this.period_id});
        this.onLoadFailure(operation);
        this.getGlobalAlertmessagelist().add({
            message: message,
            type: 'error'
        });
    },

    _setMetadata: function() {
        var periodpath = this.getPathFromBreadcrumb(this.periodRecord);
        var metatext = Ext.create('Ext.XTemplate',
            gettext('Create new assignment in <em>{period}</em>.')
        ).apply({
            period: periodpath
        });
        this.getMetainfo().update(metatext);
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
        this.getGlobalAlertmessagelist().removeAll();
        var values = this._getFormValues();
        var NON_ELECTRONIC = 1;
        if(values.delivery_types === NON_ELECTRONIC) {
            values.first_deadline = new Date(Ext.Date.now());
        }
        values.period_id = this.period_id;

        var CreateNewAssignmentModel = this.getCreateNewAssignmentModel();
        var assignment = new CreateNewAssignmentModel(values);
        this._mask();
        assignment.save({
            scope: this,
            success: this._onSuccessfulSave
        });
    },

    _onSuccessfulSave: function(record) {
        this._unmask();
        this.successPanelSetupConfig = {
            period_id: this.periodRecord.get('id'),
            periodpath : this.periodpath,
            short_name: record.get('short_name'),
            assignment_id: record.get('id')
        };
        this.application.route.navigate('/@@create-new-assignment/@@success');
    },

    _onProxyError: function(proxy, response, operation) {
        this._unmask();
        this.handleProxyError(this.getGlobalAlertmessagelist(), this.getCreateNewAssignmentForm(),
            response, operation);
    },

    _mask: function() {
        this.getCreateNewAssignmentForm().getEl().mask(gettext('Saving...'))
    },
    _unmask: function() {
        this.getCreateNewAssignmentForm().getEl().unmask();
    },

    _setInitialValues: Ext.emptyFn,

    //_setInitialValues: function() {
        //this.getCreateNewAssignmentForm().getForm().setValues({
            //long_name: 'A2',
            //short_name: 'a2'
        //})
    //},



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
