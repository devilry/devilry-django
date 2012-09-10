/**
 * Add groups on assignment.
 */
Ext.define('devilry_subjectadmin.controller.AddGroups', {
    extend: 'Ext.app.Controller',
    mixins: [
        'devilry_subjectadmin.utils.LoadAssignmentMixin',
        'devilry_subjectadmin.utils.BasenodeBreadcrumbMixin'
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
    }],

    init: function() {
        this.control({
            'addgroupsoverview': {
                render: this._onRender
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
            }
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
        this.loadAssignment(assignment_id);
    },


    //
    //
    // Load stores
    //
    //

    onLoadAssignmentSuccess: function(record) {
        this.assignmentRecord = record;
        this.getGroupsStore().setAssignment(this.assignmentRecord.get('id'));
        this._setBreadcrumb();

        this.getRelatedExaminersRoStore().setAssignment(this.assignmentRecord.get('id'));
        this.getRelatedStudentsRoStore().setAssignment(this.assignmentRecord.get('id'));

        var relatedStudentsStore = this.getRelatedStudentsRoStore();
        relatedStudentsStore.loadWithAutomaticErrorHandling({
            scope: this,
            success: this._onLoadRelatedStudentsStoreSuccess,
            errortitle: gettext('Failed to load students from the period')
        });
    },

    _handleLoadError: function(operation, title) {
        var error = Ext.create('devilry_extjsextras.DjangoRestframeworkProxyErrorHandler', operation);
        error.addErrors(null, operation);
        var errormessage = error.asHtmlList();
        Ext.widget('htmlerrordialog', {
            title: title,
            bodyHtml: errormessage
        }).show();
    },
    onLoadAssignmentFailure: function(operation) {
        this.getOverview().setLoading(false);
        this._handleLoadError(operation, gettext('Failed to load assignment'));
    },

    _onLoadRelatedStudentsStoreSuccess: function(records) {
        var relatedExaminersStore = this.getRelatedExaminersRoStore();
        relatedExaminersStore.loadWithAutomaticErrorHandling({
            scope: this,
            success: this._onLoadRelatedExaminersStoreSuccess,
            errortitle: gettext('Failed to load examiners from the period')
        });
    },

    _onLoadRelatedExaminersStoreSuccess: function() {
        this.getGroupsStore().loadWithAutomaticErrorHandling({
            scope: this,
            success: this._onLoad,
            errortitle: gettext('Failed to load groups')
        });
    },

    _onLoad: function() {
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
                text: gettext('Manage students'),
                url: devilry_subjectadmin.utils.UrlLookup.manageStudents(this.assignmentRecord.get('id'))
            }], gettext('Add students'));
        }
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
            if(this.getAutomapExaminersCheckbox().getValue() == true) {
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
            if(this.getIncludeTagsCheckbox().getValue() == true) {
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
        var ignoredcount = this.getRelatedStudentsRoStore().getTotalCount() - this.getRelatedStudentsRoStore().getCount()
        return ignoredcount;
    },

    _checkAllIgnored: function() {
        var ignoredcount = this._getIgnoredCount();
        var allIgnored = this.getRelatedStudentsRoStore().getTotalCount() == ignoredcount;
        if(allIgnored) {
            var periodinfo = this.assignmentRecord.getPeriodInfoFromBreadcrumb()
            this.getAllIgnoredHelp().setBody(periodinfo);
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

    _onSave: function(button) {
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
        console.log('sync started');
        this.getOverview().setLoading(gettext('Saving ...'));
        this.getGroupsStore().sync({
            scope: this,
            success: this._onSyncGroupsStoreSuccess,
            failure: this._onSyncGroupsStoreFailure
        });
    },

    _onSyncGroupsStoreSuccess: function(batch, options) {
        this.getOverview().setLoading(false);
        console.log('sync success', batch);
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
    },

    _onSyncGroupsStoreFailure: function(batch, options) {
        this.getOverview().setLoading(false);
        this._unmaskListOfGroups();
        console.log('failure', batch, options);
    }
});
