/**
 * Add groups on assignment.
 */
Ext.define('devilry_subjectadmin.controller.AddGroups', {
    extend: 'Ext.app.Controller',
    mixins: [
        'devilry_subjectadmin.utils.LoadAssignmentMixin',
        'devilry_subjectadmin.utils.BasenodeBreadcrumbMixin',
        'devilry_subjectadmin.utils.DjangoRestframeworkProxyErrorMixin'
    ],

    requires: [
        'Ext.tip.ToolTip',
        'devilry_subjectadmin.utils.UrlLookup'
    ],

    views: [
        'addgroups.Overview',
        'addgroups.AddGroups',
        'addgroups.AllIgnoredHelp',
        'addgroups.AllowDuplicatesCheckbox'
    ],

    models: [
        'Assignment'
    ],
    stores: [
        'RelatedStudentsRo',
        'RelatedExaminersRo',
        'Groups'
    ],

    refs: [{
        ref: 'overview',
        selector: 'addgroupsoverview'
    }, {
        ref: 'selectedStudentsGrid',
        selector: 'addgroupsoverview grid'
    }, {
        ref: 'allIgnoredHelp',
        selector: 'addgroupsoverview addgroupsallignored'
    }, {
        ref: 'allowDuplicatesCheckbox',
        selector: 'addgroupsallowduplicatescheckbox'
    }, {
        ref: 'automapExaminersCheckbox',
        selector: 'addgroupsoverview #automapExaminersCheckbox'
    }, {
        ref: 'includeTagsCheckbox',
        selector: 'addgroupsoverview #includeTagsCheckbox'
    }, {
        ref: 'tagsColumn',
        selector: 'addgroupsoverview #tagsColumn'
    }, {
        ref: 'tagsAndExaminersColumn',
        selector: 'addgroupsoverview #tagsAndExaminersColumn'
    }, {
        ref: 'saveButton',
        selector: 'addgroupsoverview #saveButton'
    }, {
        ref: 'formPanel',
        selector: 'addgroupsoverview #firstDeadlineForm'
    }, {
        ref: 'firstDeadlineField',
        selector: 'addgroupsoverview #firstDeadlineForm devilry_extjsextras-datetimefield'
    }],

    init: function() {
        this.control({
            'addgroupsoverview': {
                render: this._onRender
            },

            'addgroupsoverview addgroupspanel #studentsGrid': {
                selectionchange: this._onGridSelectionChange
            },

            'addgroupsoverview #saveButton': {
                click: this._onSave
            },
            'addgroupsoverview #selectAll': {
                click: this._onSelectAll
            },
            'addgroupsoverview #deselectAll': {
                click: this._onDeselectAll
            },
            'addgroupsallignored #allowDuplicatesButton': {
                click: this._onAllowDuplicatesButtonClick
            },
            'addgroupsoverview addgroupsallowduplicatescheckbox': {
                change: this._onAllowDuplicatesChange,
                render: this._setTooltip
            },
            'addgroupsoverview #includeTagsCheckbox': {
                change: this._onIncludeTagsChange,
                render: this._setTooltip
            },
            'addgroupsoverview #automapExaminersCheckbox': {
                change: this._onAutomapExaminersChange,
                render: this._setTooltip
            },

            'addgroupsoverview #firstDeadlineForm devilry_extjsextras-datetimefield': {
                allRendered: this._onRenderFirstDeadline,
                validitychange: this._onFirstDeadlineValidityChange
            }
        });
        this.mon(this.getAssignmentModel().proxy, {
            scope: this,
            exception: this._onAssignmentProxyError
        });
        this.mon(this.getGroupsStore().proxy, {
            scope: this,
            exception: this._onGroupsProxyError
        });
        this.mon(this.getAssignmentModel().proxy, {
            scope: this,
            exception: this._onAssignmentProxyError
        });
        this.mon(this.getRelatedStudentsRoStore().proxy, {
            scope: this,
            exception: this._onRelatedStudentsProxyError
        });
        this.mon(this.getRelatedExaminersRoStore().proxy, {
            scope: this,
            exception: this._onRelatedExaminersProxyError
        });
    },

    _setTooltip: function(item) {
        var tip = Ext.create('Ext.tip.ToolTip', {
            target: item.el,
            constrainPosition: true,
            anchor: 'top',
            dismissDelay: 30000, // NOTE: Setting this high (30sec) instead of to 0 (no autodismiss) so that it disappears eventually even when the framework do not catch the event that should hide it.
            html: item.tooltip
        });
    },

    _onRender: function() {
        var assignment_id = this.getOverview().assignment_id;
        this.on_save_success_url = this.getOverview().on_save_success_url;
        this.getOverview().setLoading(true);
        this.setLoadingBreadcrumb();
        this.getAssignmentModel().load(assignment_id, {
            scope: this,
            callback: function(record, operation) {
                if(operation.success) {
                    this.onLoadAssignmentSuccess(record);
                } // NOTE: Errors are handled in _onAssignmentProxyError
            }
        });
    },

    _onProxyError: function(response, operation) {
        if(this.getOverview() && this.getOverview().isVisible()) { // NOTE: Some of the proxies are used in many views. We only want to handle them if we are in the AddGroups view
            this.getOverview().setLoading(false);
            this.handleProxyErrorNoForm(this.application.getAlertmessagelist(), response, operation);
        }
    },
    _onAssignmentProxyError: function(proxy, response, operation) {
        this._onProxyError(response, operation);
    },
    _onGroupsProxyError: function(proxy, response, operation) {
        this._onProxyError(response, operation);
        this._loadGroupsStore(); // NOTE: Required because a failed sync will have changed the client side groups, but the remote groups are unchanged.
    },
    _onRelatedStudentsProxyError: function(proxy, response, operation) {
        this._onProxyError(response, operation);
    },
    _onRelatedExaminersProxyError: function(proxy, response, operation) {
        this._onProxyError(response, operation);
    },

    _onGridSelectionChange: function(selModel, selected) {
        this._enableSaveButtonIfOk();
    },

    _enableSaveButtonIfOk: function() {
        var selected = this.getSelectedStudentsGrid().getSelectionModel().getSelection();
        if(selected.length > 0 && this.getFirstDeadlineField().isValid()) {
            this.getSaveButton().enable();
        } else {
            this.getSaveButton().disable();
        }
    },


    //
    //
    // Load stores
    //
    //

    onLoadAssignmentSuccess: function(record) {
        this.assignmentRecord = record;
        this._setBreadcrumb();

        this.getRelatedStudentsRoStore().setAssignment(this.assignmentRecord.get('id'));
        var relatedStudentsStore = this.getRelatedStudentsRoStore();
        relatedStudentsStore.load({
            scope: this,
            callback: function(records, operation) {
                if(operation.success) {
                    this._onLoadRelatedStudentsStoreSuccess();
                } // NOTE: Failure handled in _onRelatedStudentsProxyError
            }
        });
    },

    //onLoadAssignmentFailure: function(operation) {
        //this.getOverview().setLoading(false);
    //},

    _onLoadRelatedStudentsStoreSuccess: function(records) {
        this.getRelatedExaminersRoStore().setAssignment(this.assignmentRecord.get('id'));
        var relatedExaminersStore = this.getRelatedExaminersRoStore();
        relatedExaminersStore.load({
            scope: this,
            callback: function(records, operation) {
                if(operation.success) {
                    this._onLoadRelatedExaminersStoreSuccess();
                } // NOTE: Failure handled in _onRelatedStudentsProxyError
            }
        });
    },

    _onLoadRelatedExaminersStoreSuccess: function() {
        this.getGroupsStore().setAssignment(this.assignmentRecord.get('id'));
        this._loadGroupsStore();
    },

    _loadGroupsStore: function() {
        this.getOverview().setLoading(true);
        this.getGroupsStore().load({
            scope: this,
            callback: function(records, operation) {
                if(operation.success) {
                    this._onAllLoaded();
                } // NOTE: Failure handled in _onRelatedStudentsProxyError
            }
        });
    },

    _onAllLoaded: function() {
        this.getOverview().setLoading(false);
        this.relatedExaminersMappedByTag = this.getRelatedExaminersRoStore().getMappedByTags();

        var relatedStudentsStore = this.getRelatedStudentsRoStore();
        relatedStudentsStore.clearFilter();
        this._filterOutRelatedStudentsAlreadyInGroup();
        relatedStudentsStore.sortBySpecialSorter('full_name');

        this._setBody();
    },

    _filterOutRelatedStudentsAlreadyInGroup: function() {
        var relatedStudentsStore = this.getRelatedStudentsRoStore();
        var currentUsers = this.getGroupsStore().getGroupsMappedByUserId();
        relatedStudentsStore.filterBy(function(relatedStudentRecord) {
            var userid = relatedStudentRecord.get('user').id;
            return typeof currentUsers[userid] == 'undefined';
        });
    },

    _setBreadcrumb: function() {
        var breadcrumbtype = this.getOverview().breadcrumbtype;
        if(breadcrumbtype == 'managestudents') {
            this.setSubviewBreadcrumb(this.assignmentRecord, 'Assignment', [{
                text: gettext('Students'),
                url: devilry_subjectadmin.utils.UrlLookup.manageStudents(this.assignmentRecord.get('id'))
            }], gettext('Add students'));
        }
    },

    //
    //
    // First deadline / Submission date
    //
    //
    _onRenderFirstDeadline: function() {
        this.getFirstDeadlineField().setValue(this.assignmentRecord.get('first_deadline'));
    },
    _onFirstDeadlineValidityChange: function(unused, isValid) {
        this._enableSaveButtonIfOk();
    },


    //
    //
    // Checkbox/button handlers
    //
    //

    _onSelectAll: function() {
        var selModel = this.getSelectedStudentsGrid().getSelectionModel();
        selModel.selectAll();
    },
    _onDeselectAll: function() {
        var selModel = this.getSelectedStudentsGrid().getSelectionModel();
        selModel.deselectAll();
    },

    _onAllowDuplicatesButtonClick: function() {
        this.getAllowDuplicatesCheckbox().setValue(true);
    },
    _onAllowDuplicatesChange: function(field, allowDuplicates) {
        if(allowDuplicates) {
            this.getRelatedStudentsRoStore().clearFilter();
        } else {
            this._filterOutRelatedStudentsAlreadyInGroup();
        }
        this._checkAllIgnored();
    },

    _onIncludeTagsChange: function(field, includeTags) {
        if(includeTags) {
            this.getTagsColumn().show();
            this.getAutomapExaminersCheckbox().enable();
        } else {
            if(this.getAutomapExaminersCheckbox().getValue() === true) {
                this.getAutomapExaminersCheckbox().setValue(false);
                // NOTE: we do nothing more because changing automapExaminersCheckbox will trigger _onAutomapExaminersChange
            } else {
                this.getTagsColumn().hide();
            }
            this.getAutomapExaminersCheckbox().disable();
        }
    },
    _onAutomapExaminersChange: function(field, automapExaminers) {
        if(automapExaminers) {
            this.getTagsColumn().hide();
            this.getTagsAndExaminersColumn().show();
        } else {
            //this.getTagsColumn().show();
            this.getTagsAndExaminersColumn().hide();
            if(this.getIncludeTagsCheckbox().getValue() === true) {
                this.getTagsColumn().show();
            }
        }
    },


    _setBody: function() {
        var ignoredcount = this._getIgnoredCount();
        this.getOverview().setBody({
            xtype: 'addgroupspanel',
            ignoredcount: ignoredcount,
            relatedExaminersMappedByTag: this.relatedExaminersMappedByTag,
            periodinfo: this.assignmentRecord.getPeriodInfoFromBreadcrumb()
        });
        this._checkAllIgnored();
    },

    _getIgnoredCount: function() {
        var ignoredcount = this.getRelatedStudentsRoStore().getTotalCount() - this.getRelatedStudentsRoStore().getCount();
        return ignoredcount;
    },

    _checkAllIgnored: function() {
        var ignoredcount = this._getIgnoredCount();
        var totalStudentsOnPeriod = this.getRelatedStudentsRoStore().getTotalCount();
        var allIgnored = totalStudentsOnPeriod == ignoredcount;
        if(allIgnored) {
            var periodinfo = this.assignmentRecord.getPeriodInfoFromBreadcrumb();
            this.getAllIgnoredHelp().setBody(periodinfo, totalStudentsOnPeriod);
            this.getOverview().getLayout().setActiveItem(1);
        } else {
            this.getOverview().getLayout().setActiveItem(0);
        }
    },


    //
    //
    // Save
    //
    //
    _onSave: function() {
        this.application.getAlertmessagelist().removeAll(); // Clear the list so we do not have to keep on removing errors manually.
        this.getOverview().setLoading(gettext('Saving') + ' ...');
        this._saveFirstDeadline();
    },

    _saveFirstDeadline: function() {
        var form = this.getFormPanel().getForm();
        var assignmentRecord = this.assignmentRecord;
        form.updateRecord(assignmentRecord);
        assignmentRecord.save({
            scope: this,
            callback: function(r, operation) {
                if(operation.success) {
                    this._onSaveFirstDeadlineSuccess();
                }
            }
        });
    },
    _onSaveFirstDeadlineSuccess: function() {
        this._addGroups();
    },

    _addGroups: function() {
        var selModel = this.getSelectedStudentsGrid().getSelectionModel();
        var selectedRelatedStudents = selModel.getSelection();
        var groupsStore = this.getGroupsStore();
        var includeTags = this.getIncludeTagsCheckbox().getValue();
        var automapExaminers = this.getAutomapExaminersCheckbox().getValue();

        Ext.Array.each(selectedRelatedStudents, function(relatedStudentRecord) {
            var groupRecord = groupsStore.addFromRelatedStudentRecord({
                relatedStudentRecord: relatedStudentRecord,
                includeTags: includeTags
            });
            if(automapExaminers) {
                groupRecord.setExaminersFromMapOfRelatedExaminers(this.relatedExaminersMappedByTag);
            }
        }, this);
        this._syncGroupsStore();
    },

    _syncGroupsStore: function() {
        this.getGroupsStore().sync({
            scope: this,
            success: this._onSyncGroupsStoreSuccess
            // NOTE: Failure is handled in _onGroupsProxyError
        });
    },

    _onSyncGroupsStoreSuccess: function(batch, options) {
        this.getOverview().setLoading(false);
        var affectedRecords = [];
        var operations = batch.operations;
        Ext.Array.each(operations, function(operation) {
            if(operation.action == 'create') {
                Ext.Array.each(operation.records, function(record) {
                    affectedRecords.push(record);
                }, this);
            }
        }, this);

        this.application.route.navigate(this.on_save_success_url);
    }
});
