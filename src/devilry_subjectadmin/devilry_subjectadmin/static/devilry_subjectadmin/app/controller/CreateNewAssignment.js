Ext.define('devilry_subjectadmin.controller.CreateNewAssignment', {
    extend: 'Ext.app.Controller',
    mixins: {
        'basenodeBreadcrumbMixin': 'devilry_subjectadmin.utils.BasenodeBreadcrumbMixin',
        'onLoadFailure': 'devilry_subjectadmin.utils.DjangoRestframeworkLoadFailureMixin',
        'handleProxyError': 'devilry_subjectadmin.utils.DjangoRestframeworkProxyErrorMixin'
    },

    requires: [
        'Ext.Date',
        'Ext.util.KeyNav',
        'devilry_extjsextras.NextButton',
        'devilry_extjsextras.form.ErrorUtils',
        'devilry_extjsextras.DjangoRestframeworkProxyErrorHandler',
        'devilry_subjectadmin.utils.AutoGenShortname',
        'devilry_subjectadmin.utils.UrlLookup'
    ],
    views: [
        'createnewassignment.Form',
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
        ref: 'cardPanel',
        selector: 'createnewassignmentform #cardPanel'
    }, {
        ref: 'createNewAssignment',
        selector: 'createnewassignment'
    }, {
        ref: 'globalAlertmessagelist',
        selector: 'createnewassignment alertmessagelist'
    }, {
        ref: 'pageHeading',
        selector: 'createnewassignment #pageHeading'
    }, {
        ref: 'shortNameField',
        selector: 'createnewassignmentform textfield[name=short_name]'
    }, {
        ref: 'deliveryTypesRadioGroup',
        selector: 'createnewassignmentform #deliveryTypesRadioGroup'
    }, {
        ref: 'firstDeadlineField',
        selector: 'createnewassignmentform devilry_extjsextras-datetimefield[name=first_deadline]'
    }, {
        ref: 'publishingTimeField',
        selector: 'createnewassignmentform devilry_extjsextras-datetimefield[name=publishing_time]'
    }, {
        ref: 'publishingTimeHelp',
        selector: 'createnewassignmentform #publishingTimeHelp'
    }, {
        ref: 'autoSetupExaminersField',
        selector: 'createnewassignmentform checkboxfield[name=autosetup_examiners]'
    }, {
        ref: 'addAllRelatedStudentsField',
        selector: 'createnewassignmentform checkboxfield[name=add_all_relatedstudents]'
    }, {
        ref: 'autoSetupExaminersHelp',
        selector: 'createnewassignmentform #autosetup_examiners-help'
    }],

    init: function() {
        this.control({
            'viewport createnewassignmentform': {
                render: this._onRenderCreateNewAssignmentForm
                //validitychange: this._onFormValidityChange
            },
            'viewport createnewassignmentform textfield[name=long_name]': {
                render: this._onRenderLongName,
                blur: this._onLongNameBlur
            },
            //'viewport createnewassignmentform textfield[name=short_name]': {
                //blur: this._onShortNameBlur
            //},
            'viewport createnewassignmentform #createButton': {
                click: this._onCreate
            },
            'viewport createnewassignmentform #nextButton': {
                click: this._onNext
            },
            'viewport createnewassignmentform #backButton': {
                click: this._onBack
            },
            'viewport createnewassignmentform radiogroup radio': {
                change: this._onDeliveryTypesSelect
            },
            'viewport createnewassignmentform checkboxfield[name=add_all_relatedstudents]': {
                change: this._onAddRelatedStudentChange
            }
            //'viewport createnewassignmentform #firstDeadlineField': {
                //change: this._onFirstDeadlineChange
            //}
        });
    },

    _onLongNameBlur: function(field) {
        var shortnamefield = this.getShortNameField();
        if(shortnamefield.getValue() == '') {
            var value = field.getValue();
            var short_name = devilry_subjectadmin.utils.AutoGenShortname.autogenShortname(value);
            shortnamefield.setValue(short_name);
        }
    },
    //_onShortNameBlur: function() {
    //},

    //_onFirstDeadlineChange: function(field, newValue, oldValue) {
        //console.log(newValue, oldValue);
    //},

    //_onFormValidityChange: function(basicform, valid) {
        //console.log(valid);
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
        this.setLoadingBreadcrumb();
        this.getCreateNewAssignmentForm().keyNav = Ext.create('Ext.util.KeyNav', this.getCreateNewAssignmentForm().el, {
            enter: this._onHitEnter,
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

    _onHitEnter: function() {
        var itemId = this.getCardPanel().getLayout().getActiveItem().itemId;
        if(this._isValid()) {
            if(itemId == 'pageOne') {
                this._onNext();
            } else {
                this._onCreate();
            }
        }
    },

    _onNext: function() {
        this.getGlobalAlertmessagelist().removeAll(); // NOTE: If we fail validation, we redirect to page one. If users fix errors there, it would seem strange when they continue to display on page2.
        this.getCardPanel().getLayout().setActiveItem(1);
    },
    _onBack: function() {
        this.getCardPanel().getLayout().setActiveItem(0);
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
        this._updateHeader();
        this.setSubviewBreadcrumb(this.periodRecord, 'Period', [], gettext('Create new assignment'));
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

    _updateHeader: function() {
        var periodpath = this.getPathFromBreadcrumb(this.periodRecord);
        this.getPageHeading().update({
            heading: gettext('Create new assignment'),
            subheading: periodpath
        });
    },

    _onDeliveryTypesSelect: function(radio, records) {
        var is_electronic = radio.getGroupValue() === 0;
        if(is_electronic) {
            this.getFirstDeadlineField().show();
            this.getPublishingTimeField().show();
            this.getPublishingTimeHelp().show();
            this.getFirstDeadlineField().setValue(null); // NOTE: See note in the else section below
        } else {
            this.getFirstDeadlineField().hide();
            this.getPublishingTimeField().hide();
            this.getPublishingTimeHelp().hide();
            this.getFirstDeadlineField().setValue(new Date()); // NOTE: Set datetime to make sure the field validates - we clear it when we show the field again, and the value is not submitted as long as the type is non-electronic.
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

    _isValid: function() {
        return this.getCreateNewAssignmentForm().getForm().isValid();
    },

    _onCreate: function() {
        if(this._isValid()) {
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
            values.first_deadline = null;
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
        this.application.route.navigate(devilry_subjectadmin.utils.UrlLookup.assignmentOverview(record.get('id')));
    },

    _onProxyError: function(proxy, response, operation) {
        this._unmask();
        this.handleProxyError(this.getGlobalAlertmessagelist(), this.getCreateNewAssignmentForm(),
            response, operation);
        this.getCardPanel().getLayout().setActiveItem(0);
    },

    _mask: function() {
        this.getCreateNewAssignmentForm().getEl().mask(gettext('Saving...'))
    },
    _unmask: function() {
        this.getCreateNewAssignmentForm().getEl().unmask();
    },

    _setInitialValues: Ext.emptyFn

    //_setInitialValues: function() {
        //Ext.defer(function() {
            //this.getCreateNewAssignmentForm().getForm().setValues({
                //long_name: 'A2',
                //short_name: 'a2',
                //first_deadline: new Date()
            //});
        //}, 300, this);
    //}
});
