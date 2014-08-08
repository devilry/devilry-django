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

    stores: ['Assignments'],

    refs: [{
        ref: 'globalAlertmessagelist',
        selector: '#appAlertmessagelist'
    }, {
        ref: 'createNewAssignmentForm',
        selector: 'createnewassignmentform'
    }, {
        ref: 'cardPanel',
        selector: 'createnewassignmentform #cardPanel'
    }, {
        ref: 'createNewAssignment',
        selector: 'createnewassignment'
    }, {
        ref: 'pageHeading',
        selector: 'createnewassignment #pageHeading'
    }, {
        ref: 'shortNameField',
        selector: 'createnewassignmentform textfield[name=short_name]'
    }, {
        ref: 'longNameField',
        selector: 'createnewassignmentform textfield[name=long_name]'
    }, {
        ref: 'deliveryTypesRadioGroup',
        selector: 'createnewassignmentform #deliveryTypesRadioGroup'
    }, {
        ref: 'firstDeadlineField',
        selector: 'createnewassignmentform devilry_extjsextras-datetimefield[name=first_deadline]'
    }, {
        ref: 'firstDeadlineHelp',
        selector: 'createnewassignmentform #firstDeadlineHelp'
    }, {
        ref: 'publishingTimeField',
        selector: 'createnewassignmentform devilry_extjsextras-datetimefield[name=publishing_time]'
    }, {
        ref: 'publishingTimeHelp',
        selector: 'createnewassignmentform #publishingTimeHelp'
    }, {
        ref: 'advancedOptionsPanel',
        selector: 'createnewassignmentform #advancedOptionsPanel'
    }, {

    // Page two
        ref: 'setupExaminersContainer',
        selector: 'createnewassignmentform #setupExaminersContainer'
    }, {
        ref: 'selectAssignmentToCopyStudentsFrom',
        selector: 'createnewassignmentform #selectAssignmentToCopyStudentsFrom'
    }, {
        ref: 'selectAssignmentToCopyStudentsFromCombo',
        selector: 'createnewassignmentform #selectAssignmentToCopyStudentsFrom selectsingleassignment'
    }, {
        ref: 'setupStudentsCopyFromAssignmentRadio',
        selector: 'createnewassignmentform #setupStudentsCopyFromAssignmentRadio'
    }, {
        ref: 'setupStudentsAllRelatedRadio',
        selector: 'createnewassignmentform #setupStudentsAllRelatedRadio'
    }, {
        ref: 'setupExaminersCopyFromAssignmentRadio',
        selector: 'createnewassignmentform #setupExaminersCopyFromAssignmentRadio'
    }, {
        ref: 'setupExaminersByTagsRadio',
        selector: 'createnewassignmentform #setupExaminersByTagsRadio'
    }, {
        ref: 'setupExaminersByTagsHelp',
        selector: 'createnewassignmentform #setupExaminersByTagsHelp'
    }],

    ui_datetimeformat: 'Y-m-d H:i',
    transport_datetimeformat: 'Y-m-dTH:i',

    init: function() {
        this.control({
            'viewport createnewassignmentform textfield[name=long_name]': {
                render: this._onRenderLongName,
                blur: this._onLongNameBlur
            },

            // Page one
            'viewport createnewassignmentform #nextButton': {
                click: this._onNext
            },
            'viewport createnewassignmentform #deliveryTypesRadioGroup radio': {
                change: this._onDeliveryTypesSelect
            },
            'viewport createnewassignmentform devilry_extjsextras-datetimefield[name=publishing_time] devilry_extjsextras_datefield': {
                change: this._onPublishingTimeDateFieldChange
            },

            // Page 2
            'viewport createnewassignmentform #backButton': {
                click: this._onBack
            },
            'viewport createnewassignmentform #createButton': {
                click: this._onCreate
            },
            'viewport createnewassignmentform #studentsSetupRadiogroup': {
                change: this._onStudentsSetupRadiogroupChange
            },
            'viewport createnewassignmentform selectsingleassignment[name=copyfromassignment_id]': {
                change: this._onSelectAssignmentToCopyFromChange
            }
        });
    },

    _mask: function(text) {
        this.getCreateNewAssignmentForm().setLoading(text);
    },
    _unmask: function() {
        this.getCreateNewAssignmentForm().setLoading(false);
    },


    _onHitEnter: function() {
        var itemId = this.getCardPanel().getLayout().getActiveItem().itemId;
        if(this._isValid()) {
            if(itemId === 'pageOne') {
                this._onNext();
            } else {
                this._onCreate();
            }
        }
    },


    // 
    //
    // Load
    //
    //

    _onLoadFailure: function(operation) {
        this._unmask();
        this.onLoadFailure(operation);
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
        this._loadAssignments();
    },
    _onLoadPeriodFailure: function(operation) {
        this._onLoadFailure(operation);
    },

    _loadAssignments: function() {
        this.getAssignmentsStore().loadAssignmentsInPeriod(this.periodRecord.get('id'), this._onLoadAssignments, this);
    },
    _onLoadAssignments: function(assignmentRecords, operation) {
        if(operation.success) {
            this._onLoadAssignmentsSuccess(assignmentRecords);
        } else {
            this._onLoadFailure(operation);
        }
    },

    _applyInitialValues: function(initialValues) {
        //initialValues.first_deadline = new Date();
        //var qry = Ext.Object.fromQueryString(window.location.search);
        var defaults = this.getCreateNewAssignment().defaults;
//        initialValues.publishing_time = this._detectSanePublishingTime();
        if(Ext.isEmpty(defaults)) {
            return;
        }
        var qry = Ext.Object.fromQueryString(defaults);
        if(!Ext.isEmpty(qry.first_deadline)) {
            initialValues.first_deadline = Ext.Date.parse(qry, this.transport_datetimeformat);
        }
        if(!Ext.isEmpty(qry.delivery_types)) {
            initialValues.delivery_types = parseInt(qry.delivery_types, 10);
        }
        if(!Ext.isEmpty(qry.setupstudents_mode)) {
            initialValues.setupstudents_mode = qry.setupstudents_mode;
        }
        if(!Ext.isEmpty(qry.setupexaminers_mode)) {
            initialValues.setupexaminers_mode = qry.setupexaminers_mode;
        }
        if(!Ext.isEmpty(qry.copyfromassignment_id)) {
            initialValues.copyfromassignment_id = parseInt(qry.copyfromassignment_id, 10);
        }
        if(!Ext.isEmpty(qry.only_copy_passing_groups)) {
            initialValues.only_copy_passing_groups = qry.only_copy_passing_groups === 'true';
        }
        if(!Ext.isEmpty(qry.anonymous)) {
            initialValues.anonymous = qry.anonymous === 'true';
        }
    },
    _onLoadAssignmentsSuccess: function(assignmentRecords) {
        var initialValues = {};

        this._autoapplyIntialValues(initialValues);

        if(assignmentRecords.length > 0) {
            this.getSetupStudentsCopyFromAssignmentRadio().show();
            initialValues.copyfromassignment_id = assignmentRecords[0].get('id');
        }
        this._applyInitialValues(initialValues);
        this.getCreateNewAssignmentForm().getForm().setValues(initialValues);
        Ext.defer(function() {
            // NOTE: Using defer to clear the error-marks added when we setValues above
            this._onFullyRenderedAndInitialized(initialValues);
        }, 200, this);
    },

    _onFullyRenderedAndInitialized: function(initialValues) {

        var timefield = this.getFirstDeadlineField().down('devilry_extjsextras_timefield');
        if(timefield.getValue() === null) {
            timefield.setValue('23:59');
        }

        // this._syncPubtimeAndFirstDeadline(); // NOTE: not needed because this is triggered on load by _onPublishingTimeDateFieldChange when we set publishing_time
        var datefield = this.getFirstDeadlineField().down('devilry_extjsextras_datefield');
        datefield.clearInvalid(); // Important: this must come after we have set all values on the datetime field

        // NOTE: Using defer avoids that the text style remains
        // emptyText-gray (I assume it does no because render is fired
        // before the style is applied).
        //this.getLongNameField().focus();
        this.getLongNameField().selectText();

        if(initialValues.anonymous) {
            this.getAdvancedOptionsPanel().expand();
        }
        var assignmentId = this.getSelectAssignmentToCopyStudentsFromCombo().getValue();
        this._unmask();
    },


    _onPublishingTimeDateFieldChange: function() {
        this._syncPubtimeAndFirstDeadline();
    },

    _syncPubtimeAndFirstDeadline: function() {
        var pubtime_datefield = this.getPublishingTimeField().down('devilry_extjsextras_datefield');
        pubtime_datefield.setMinValue(new Date());
        pubtime_datefield.setMaxValue(this.periodRecord.get('end_time'));

        var first_deadline_datefield = this.getFirstDeadlineField().down('devilry_extjsextras_datefield');
        var pubdate = pubtime_datefield.getValue();
        if(pubdate !== null) {
            first_deadline_datefield.setMinValue(pubtime_datefield.getValue());
            var first_deadline_date = first_deadline_datefield.getValue();
            if(first_deadline_date !== null) {
                if(pubdate > first_deadline_date) {
                    first_deadline_datefield.validate();
                    this.application.getAlertmessagelist().add({
                        type: 'warning',
                        autoclose: true,
                        message: gettext('The publishing time is set to a later date than the submission date.')
                    });
                }
            }
        }
        first_deadline_datefield.setMaxValue(this.periodRecord.get('end_time'));
    },


    _em: function(string) {
        return Ext.String.format('<em>{0}</em>', string);
    },

    _autoapplyIntialValues: function(initialValues) {
        var autoSummary = [];
        this._autoapplyNamesFromLastAssignment(initialValues, autoSummary);
        this._autoapplyFirstDeadline(initialValues, autoSummary);
        this._autoapplyPublishingTime(initialValues, autoSummary);
        if(autoSummary.length === 0) {
            return;
        }

        var labelsList = [];
        var detailsList = [];
        Ext.Array.each(autoSummary, function(summary) {
            labelsList.push(this._em(summary.label));
            detailsList.push(Ext.String.format('<h2>{0}</h2>', summary.label));
            detailsList.push(Ext.create('Ext.XTemplate', summary.detailstpl).apply(summary.detailsdata));
        }, this);

        this.application.getAlertmessagelist().add({
            type: 'info',
            autoclose: 6,
            messagetpl: [
                gettext('Devilry suggested values for: {labels}.'),
                ' <small>{MORE_BUTTON}</small>',
                '<div {MORE_ATTRS}>{details}</div>'
            ],
            messagedata: {
                labels: labelsList.join(', '),
                details: detailsList.join('')
            }
        });
    },

    _autoapplyNamesFromLastAssignment: function(initialValues, autoSummary) {
        if(this.getAssignmentsStore().getCount() === 0) {
            return;
        }
        var lastAssignment = this.getAssignmentsStore().first();
        var last_short_name = lastAssignment.get('short_name');
        var last_long_name = lastAssignment.get('long_name');
        var last_shortname_number = this._getNumberInName(last_short_name);
        var last_longname_number = this._getNumberInName(last_long_name);
        if(last_shortname_number === last_longname_number && last_shortname_number !== null) {
            var oldnumber = parseInt(last_shortname_number, 10);
            var number = oldnumber + 1;
            var short_name = last_short_name.replace(oldnumber.toString(), number.toString());
            var long_name = last_long_name.replace(oldnumber.toString(), number.toString());
            Ext.apply(initialValues, {
                long_name: long_name,
                short_name: short_name
            });

            autoSummary.push({
                label: gettext('Name'),
                detailstpl: [
                    '<p>',
                        gettext('Suggested {long_name} as the name, based on {last_long_name}.'),
                    '</p>'
                ],
                detailsdata: {
                    last_long_name: Ext.String.format('<em>{0}</em>', last_long_name),
                    long_name: Ext.String.format('<em>{0}</em>', long_name)
                }
            });
        }
    },

    _autoapplyFirstDeadline: function(initialValues, autoSummary) {
        var result = this.getAssignmentsStore().smartAutodetectFirstDeadline();
        if(result !== null) {
            initialValues.first_deadline = result.detectedDateTime;

            var previous_first_deadline = result.lastAssignment.get('first_deadline');
            autoSummary.push({
                label: gettext('Submission date'),
                detailstpl: [
                    '<p>',
                        gettext('Calculated by adding the most common timespan between submission dates ({days} days) to the submission date of the last published assignment, {previous_assignment} ({previous_first_deadline}).'),
                    '</p>',
                    '<tpl if="hasExtraDelay">',
                        '<p>',
                            gettext('You have a break in the regular timespan. Since you use a short interval between 1 day and 14 days, we assume this means you have skipped an interval or two, and suggested a submission date based on those assumptions.'),
                        '</p>',
                    '</tpl>'
                ],
                detailsdata: {
                    days: result.mostCommonDayDiff.days,
                    previous_assignment: this._em(result.lastAssignment.get('short_name')),
                    previous_first_deadline: devilry_extjsextras.DatetimeHelpers.formatDateTimeShort(previous_first_deadline),
                    hasExtraDelay: result.delayCount > 1
                }
            });
        }
    },

    _autoapplyPublishingTime:function (initialValues, autoSummary) {
        initialValues.publishing_time = new Date();
        // var result = this.getAssignmentsStore().smartAutodetectPublishingTime();
        // if(result === null) {
        //     initialValues.publishing_time = this.getAssignmentsStore().getUniqueFuturePublishingTime();
        // } else {
        //     initialValues.publishing_time = result.detectedDateTime;
        //     var previous_publishing_time = result.lastAssignment.get('publishing_time');
        //     autoSummary.push({
        //         label: gettext('Publishing time'),
        //         detailstpl: [
        //             '<p>',
        //             gettext('Calculated by adding the most common timespan between publishing times ({days} days) to the publishing time of the last published assignment, {previous_assignment} ({previous_publishing_time}).'),
        //             '</p>',
        //             '<tpl if="hasExtraDelay">',
        //             '<p>',
        //             gettext('You have a break in the regular timespan. Since you use a short interval between 1 day and 14 days, we assume this means you have skipped an interval or two, and suggested a publishing time based on those assumptions.'),
        //             '</p>',
        //             '</tpl>'
        //         ],
        //         detailsdata: {
        //             days: result.mostCommonDayDiff.days,
        //             previous_assignment: this._em(result.lastAssignment.get('short_name')),
        //             previous_publishing_time: devilry_extjsextras.DatetimeHelpers.formatDateTimeShort(previous_publishing_time),
        //             hasExtraDelay: result.delayCount > 1
        //         }
        //     });
        // }
    },

    _getNumberInName: function(name) {
        var numbers = name.match(/\d+/);
        if(numbers !== null && numbers.length === 1) {
            return numbers[0];
        } else {
            return null;
        }
    },


    //
    //
    // Render
    //
    //
    _onRenderLongName: function() {
        this.setLoadingBreadcrumb();
        this._mask(gettext('Loading') + ' ...');
        this.getCreateNewAssignmentForm().keyNav = Ext.create('Ext.util.KeyNav', this.getCreateNewAssignmentForm().el, {
            enter: this._onHitEnter,
            scope: this
        });

        this.getCreateNewAssignmentForm().mon(this.getCreateNewAssignmentModel().proxy, {
            scope: this,
            exception: this._onProxyError
        });
        this.period_id = this.getCreateNewAssignment().period_id;
        this._loadPeriod(this.period_id);
    },

    _updateHeader: function() {
        var periodpath = this.getPathFromBreadcrumb(this.periodRecord);
        this.getPageHeading().update({
            heading: gettext('Create new assignment'),
            subheading: periodpath
        });
    },


    //
    //
    // Page one
    //
    //

    _onDeliveryTypesSelect: function(radio, records) {
        var is_electronic = radio.getGroupValue() === 0;
        if(is_electronic) {
            this.getFirstDeadlineField().show();
            this.getFirstDeadlineHelp().show();
            this.getPublishingTimeField().show();
            this.getPublishingTimeHelp().show();
            if(!this.getFirstDeadlineField().isValid()) {
                this.getFirstDeadlineField().setValue(null); // NOTE: See note in the else section below
            }
        } else {
            this.getFirstDeadlineField().hide();
            this.getFirstDeadlineHelp().hide();
            this.getPublishingTimeField().hide();
            this.getPublishingTimeHelp().hide();
            if(!this.getFirstDeadlineField().isValid()) {
                this.getFirstDeadlineField().setValue(new Date()); // NOTE: Set datetime to make sure the field validates - we clear it when we show the field again, and the value is not submitted as long as the type is non-electronic.
            }
        }
    },

    _onLongNameBlur: function(field) {
        var shortnamefield = this.getShortNameField();
        if(shortnamefield.getValue() === '') {
            var value = field.getValue();
            var short_name = devilry_subjectadmin.utils.AutoGenShortname.autogenShortname(value);
            shortnamefield.setValue(short_name);
        }
    },

    _onNext: function() {
        this.getGlobalAlertmessagelist().removeAll(); // NOTE: If we fail validation, we redirect to page one. If users fix errors there, it would seem strange when they continue to display on page2.
        this.getCardPanel().getLayout().setActiveItem(1);
    },



    //
    //
    // Page two
    //
    //

    _onBack: function() {
        this.getCardPanel().getLayout().setActiveItem(0);
    },

    _labelExaminerCopyFromAssignment: function() {
        var assignmentId = this.getSelectAssignmentToCopyStudentsFromCombo().getValue();
        var store = this.getAssignmentsStore();
        var index = store.findExact('id', assignmentId);
        if(index === -1) {
            // NOTE: If an invalid assignment is selected (typically from
            // defaults), we autoselect the first assignment in the store,
            // which should trigger _onSelectAssignmentToCopyFromChange, which
            // re-triggers this function.
            this.getSelectAssignmentToCopyStudentsFromCombo().setValue(store.first().get('id'));
            return;
        }
        var assignmentRecord = store.getAt(index);
        var label = interpolate(gettext('Copy from %(assignment)s.'), {
            assignment: assignmentRecord.get('long_name')
        }, true);
        var radio = this.getSetupExaminersCopyFromAssignmentRadio();
        radio.boxLabelEl.setHTML(label);
    },

    _hilight: function(component) {
        Ext.create('Ext.fx.Animator', {
            target: component.getEl(),
            duration: 2000,
            keyframes: {
                0: {
                    backgroundColor: '#FFFFFF'
                },
                20: {
                    backgroundColor: '#FBEED5'
                },
                50: {
                    backgroundColor: '#FBEED5'
                },
                100: {
                    backgroundColor: '#FFFFFF'
                }
            }
        });
    },

    _onStudentsSetupRadiogroupChange: function(unused, newValue, oldValue) {
        var setupstudents_mode = newValue.setupstudents_mode;
        var old_setupstudents_mode = oldValue.setupstudents_mode;

        
        this.getSelectAssignmentToCopyStudentsFrom().hide();
        this.getSetupExaminersCopyFromAssignmentRadio().hide();

        this.getSetupExaminersByTagsRadio().hide();
        this.getSetupExaminersByTagsHelp().hide();

        if(setupstudents_mode === 'copyfromassignment') {
            this.getSelectAssignmentToCopyStudentsFrom().show();
            this.getSetupExaminersCopyFromAssignmentRadio().show();
            this._labelExaminerCopyFromAssignment();
            this.getSetupExaminersCopyFromAssignmentRadio().setValue(true);
            this._hilight(this.getSetupExaminersCopyFromAssignmentRadio());
        } else if(setupstudents_mode === 'allrelated') {
            this.getSetupExaminersByTagsRadio().show();
            this.getSetupExaminersByTagsHelp().show();
            this.getSetupExaminersByTagsRadio().setValue(true);
            this._hilight(this.getSetupExaminersByTagsRadio());
        }

        // Hide examiner setup panel if not setting up students
        if(setupstudents_mode === 'do_not_setup') {
            this.getSetupExaminersContainer().hide();
        } else {
            this.getSetupExaminersContainer().show();
        }
    },

    _onSelectAssignmentToCopyFromChange: function(combo, newValue) {
        this._labelExaminerCopyFromAssignment();
    },



    //
    //
    // Save
    //
    //

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
        this._mask(gettext('Saving') + ' ...');
        assignment.save({
            scope: this,
            success: this._onSuccessfulSave
        });
    },

    _onSuccessfulSave: function(record) {
        this._unmask();
        this.application.addOnNextRouteMessage({
            type: 'success',
            messagetpl: [
                gettext('Created {name}.'),
                ' <a href="{url}">',
                    gettext('Create another assignment'),
                '</a>.'
            ],
            messagedata: {
                name: Ext.String.format('<em>{0}</em>', record.get('long_name')),
                url: devilry_subjectadmin.utils.UrlLookup.createNewAssignment(this.periodRecord.get('id'), {
                    anonymous: record.get('anonymous'),
                    delivery_types: record.get('delivery_types'),
                    setupstudents_mode: record.get('setupstudents_mode'),
                    setupexaminers_mode: record.get('setupexaminers_mode'),
                    copyfromassignment_id: record.get('copyfromassignment_id'),
                    only_copy_passing_groups: record.get('only_copy_passing_groups')
                })
            }
        });
        this.application.route.navigate(devilry_subjectadmin.utils.UrlLookup.assignmentOverview(record.get('id')));
    },

    _onProxyError: function(proxy, response, operation) {
        this._unmask();
        this.handleProxyError(this.getGlobalAlertmessagelist(), this.getCreateNewAssignmentForm(),
            response, operation);
        this.getCardPanel().getLayout().setActiveItem(0);
    }
});
