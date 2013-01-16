/**
 * Passed previous period wizard
 */
Ext.define('devilry_subjectadmin.controller.PassedPreviousPeriodController', {
    extend: 'Ext.app.Controller',
    mixins: [
        'devilry_subjectadmin.utils.BasenodeBreadcrumbMixin',
        'devilry_subjectadmin.utils.DjangoRestframeworkProxyErrorMixin',
        'devilry_subjectadmin.utils.LoadAssignmentMixin',
        'devilry_subjectadmin.utils.DjangoRestframeworkLoadFailureMixin',
        'devilry_subjectadmin.utils.LoadGradeEditorMixin'
    ],

    requires: [
        'devilry.gradeeditors.EditManyDraftEditorWindow',
        'devilry_extjsextras.DjangoRestframeworkProxyErrorHandler'
    ],

    views: [
        'passedpreviousperiod.PassedPreviousPeriodOverview'
    ],

    models: [
        'Assignment',
        'GradeEditorConfig',
        'GradeEditorRegistryItem'
    ],
    stores: ['PassedPreviousPeriodItems'],

    refs: [{
        ref: 'globalAlertmessagelist',
        selector: '#appAlertmessagelist'
    }, {
        ref: 'overview',
        selector: 'passedpreviousperiodoverview'
    }, {
        ref: 'cardContainer',
        selector: 'passedpreviousperiodoverview #cardContainer'
    }, {
        ref: 'unsupportedGradeEditor',
        selector: 'passedpreviousperiodoverview #unsupportedGradeEditor'

    // Page one
    }, {
        ref: 'groupsGrid',
        selector: 'passedpreviousperiodoverview #pageOne selectpassedpreviousgroupsgrid'
    }, {
        ref: 'showUnRecommendedCheckbox',
        selector: 'passedpreviousperiodoverview #pageOne #showUnRecommendedCheckbox'
    }, {
        ref: 'nextButton',
        selector: 'passedpreviousperiodoverview #pageOne #nextButton'

    // Page two
    }, {
        ref: 'pageTwo',
        selector: 'passedpreviousperiodoverview #pageTwo'
    }, {
        ref: 'confirmGroupsGrid',
        selector: 'passedpreviousperiodoverview confirmpassedpreviousgroupsgrid'
    }],

    init: function() {
        this.control({
            'passedpreviousperiodoverview': {
                render: this._onRender
            },

            // Page one
            'passedpreviousperiodoverview #pageOne selectpassedpreviousgroupsgrid': {
                selectionchange: this._onGroupsSelectionChange
            },
            'passedpreviousperiodoverview #pageOne #showUnRecommendedCheckbox': {
                change: this._onShowUnRecommendedCheckbox
            },
            'passedpreviousperiodoverview #pageOne #nextButton': {
                click: this._onNextButton
            },

            // Page two
            'passedpreviousperiodoverview #pageTwo #backButton': {
                click: this._onBackButton
            },
            'passedpreviousperiodoverview #pageTwo #saveButton': {
                click: this._onSave
            }
        });
    },

    _onRender: function() {
        this.setLoadingBreadcrumb();
        this.getOverview().setLoading(true);
        this.assignment_id = this.getOverview().assignment_id;
        this.loadAssignment(this.assignment_id);
    },

    _onAssignmentProxyError: function(proxy, response, operation) {
        this._onProxyError(response, operation);
    },
    onLoadAssignmentSuccess: function(record) {
        this.assignmentRecord = record;

        var text = gettext('Passed previously');
        this.setSubviewBreadcrumb(this.assignmentRecord, 'Assignment', [], text);
        var path = this.getPathFromBreadcrumb(this.assignmentRecord);
        this.application.setTitle(Ext.String.format('{0}.{1}', path, text));

        var gradeeditor = this.assignmentRecord.get('gradeeditor');
        if(gradeeditor.shortformat === null) {
            this.getOverview().setLoading(false);
            this.getUnsupportedGradeEditor().updateData({
                gradingsystem: Ext.String.format('<em>{0}</em>', gradeeditor.title)
            });
            this._setPage('unsupportedGradeEditor');
        } else {
            this._loadStore();
        }
    },
    onLoadAssignmentFailure: function(operation) {
        this.getOverview().setLoading(false);
        this.onLoadFailure(operation);
    },

    _setPage: function(itemId) {
        this.getCardContainer().getLayout().setActiveItem(itemId);
    },



    //
    //
    // Load store
    //
    //
    _loadStore: function() {
        this.getPassedPreviousPeriodItemsStore().loadGroupsInAssignment(this.assignment_id, {
            scope: this,
            callback: this._onLoadStore
        });
    },

    _onLoadStore: function(records, operation) {
        this.getOverview().setLoading(false);
        if(operation.success) {
            this._applyPageOneFilters();
            var displayedGroups = this.getPassedPreviousPeriodItemsStore().getCount();
            if(displayedGroups === 0) {
                this._handleNoDisplayedGroups();
            }

            var store = this.getPassedPreviousPeriodItemsStore();
            store.each(function(record) {
                record.set('newfeedback_shortformat', record.get('oldgroup').feedback_shortformat);
                record.commit();
            });

            this.getGroupsGrid().selectWithPassingGradeInPrevious();
            this.getConfirmGroupsGrid().addEditColumn(this.assignmentRecord.get('gradeeditor'));
        } else {
            this.onLoadFailure(operation);
        }
    },


    //
    //
    // Page 1
    //
    //
    _onGroupsSelectionChange: function(selModel, selected) {
        if(selected.length === 0) {
            this.getNextButton().disable();
        } else {
            this.getNextButton().enable();
        }
    },

    _handleNoDisplayedGroups:function () {
        this.application.getAlertmessagelist().add({
            type: 'warning',
            extracls: 'no-nonignoredgroups-warning',
            message: gettext('We did not detect any groups that Devilry does not believe should be ignored. Use the checkbox below the grid to see and select ignored groups.')
        });
    },

    _applyPageOneFilters: function() {
        var store = this.getPassedPreviousPeriodItemsStore();
        store.clearFilter();
        if(!this.getShowUnRecommendedCheckbox().getValue()) {
            store.filterBy(function(record) {
                var whyignored = record.get('whyignored');
                if(!Ext.isEmpty(whyignored)) {
                    return !(whyignored === 'has_alias_feedback' ||
                        whyignored === 'has_feedback' ||
                        whyignored === 'only_failing_grade_in_previous');
                } else {
                    return true;
                }
            });
        }
    },

    _onShowUnRecommendedCheckbox: function() {
        this._applyPageOneFilters();
    },

    _onNextButton: function() {
        var store = this.getPassedPreviousPeriodItemsStore();
        var selModel = this.getGroupsGrid().getSelectionModel();
        store.filterBy(function(record) {
            return selModel.isSelected(record);
        });
        this._setPage('pageTwo');
    },

    //
    //
    // Page 2
    //
    //
    _onBackButton: function() {
        this._applyPageOneFilters();
        this._setPage('pageOne');
    },

    _onSave: function() {
        var store = this.getPassedPreviousPeriodItemsStore();
        store.each(function(record) {
            var oldgroup = record.get('oldgroup');
//            if(Ext.isEmpty(oldgroup)) {
//                var feedback = {
//                    grade: 'Approved',
//                    points: 1,
//                    is_passing_grade: true,
//                    rendered_view: ''
//                };
//                record.set('feedback', feedback);
//            } else {
//                record.set('feedback', null);
//                record.setDirty();
//            }
            record.setDirty(); // We want to push all records, not just those with changes
        }, this);
        this.getOverview().setLoading(gettext('Saving') + ' ...');
        store.sync({
            scope: this,
            success: function(batch, options) {
                this._onSyncSuccess(batch, options);
            },
            failure: function(batch, options) {
                this._onSyncFailure(batch, options);
            }
        });
    },

    _onSyncSuccess: function(batch, options, callbackconfig) {
        this.getOverview().setLoading(false);
        var store = this.getPassedPreviousPeriodItemsStore();
        var count = store.getCount();
        this.application.getAlertmessagelist().add({
            type: 'success',
            autoclose: true,
            message: interpolate(gettext('Marked %(count)s groups as previously passed.'), {
                count: count
            }, true)
        });
        this._onBackButton();
        this._loadStore();
    },

    _onSyncFailure: function(batch, options) {
        this.getOverview().setLoading(false);
        var error = Ext.create('devilry_extjsextras.DjangoRestframeworkProxyErrorHandler');
        error.addBatchErrors(batch);
        var messages = [];
        var validationErrors = 0;
        Ext.Array.each(batch.exceptions, function(exception) {
            if(exception.error.status === 400) {
                validationErrors ++;
            } else {
                var message = error.parseHttpError(exception.error, exception.request);
                messages.push(message);
            }
        }, this);
        if(messages.length > 0) {
            this.application.getAlertmessagelist().addMany(messages, 'error');
        }
        if(validationErrors > 0) {
            this.application.getAlertmessagelist().add({
                type: 'error',
                messagetpl: [
                    gettext('{errorcount} groups has an invalid grade. Please review the help for the grade format in the sidebar.')
                ],
                messagedata: {
                    errorcount: validationErrors
                }
            });
        }
    }
});
