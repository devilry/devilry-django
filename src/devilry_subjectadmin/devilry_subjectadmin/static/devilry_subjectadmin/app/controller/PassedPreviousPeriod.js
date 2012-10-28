/**
 * Passed previous period wizard
 */
Ext.define('devilry_subjectadmin.controller.PassedPreviousPeriod', {
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
        'passedpreviousperiod.Overview'
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

        this.loadGradeEditorRecords(this.assignmentRecord.get('id'));
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
    // Load grade editor
    //
    //

    onLoadGradeEditorSuccess: function(gradeEditorConfigRecord, gradeEditorRegistryItemRecord) {
        this.gradeEditorConfigRecord = gradeEditorConfigRecord;
        this.gradeEditorRegistryItemRecord = gradeEditorRegistryItemRecord;
        var gradeeditorid = this.gradeEditorConfigRecord.get('gradeeditorid');
        if(gradeeditorid !== 'approved') {
            this.getOverview().setLoading(false);
            this._setPage('unsupportedGradeEditor');
        } else {
            this._loadStore();
        }
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
            this.getGroupsGrid().selectWithPassingGradeInPrevious();
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
            if(Ext.isEmpty(oldgroup)) {
                var feedback = {
                    grade: 'Approved',
                    points: 1,
                    is_passing_grade: true,
                    rendered_view: ''
                };
                record.set('feedback', feedback);
            } else {
                record.set('feedback', null);
                record.setDirty();
            }
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
        var messages = error.asArrayOfStrings();
        this.application.getAlertmessagelist().addMany(messages, 'error');
    }
});
