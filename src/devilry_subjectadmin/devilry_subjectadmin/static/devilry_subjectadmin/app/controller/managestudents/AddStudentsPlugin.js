/**
 * Plugin for {@link devilry_subjectadmin.controller.managestudents.Overview} that
 * adds the ability to add students (groups with a single student) to an
 * assignment.
 */
Ext.define('devilry_subjectadmin.controller.managestudents.AddStudentsPlugin', {
    extend: 'Ext.app.Controller',

    views: [
        'managestudents.AddStudentsWindow',
    ],

    stores: [
        'RelatedStudentsRo',
        'RelatedExaminersRo',
        'Groups'
    ],

    requires: [
        'Ext.tip.ToolTip'
    ],

    refs: [{
        ref: 'addStudentsWindow',
        selector: 'addstudentswindow'
    }, {
        ref: 'selectedStudentsGrid',
        selector: 'addstudentswindow grid'
    }, {
        ref: 'automapExaminersCheckbox',
        selector: 'addstudentswindow #automapExaminersCheckbox'
    }, {
        ref: 'includeTagsCheckbox',
        selector: 'addstudentswindow #includeTagsCheckbox'
    }, {
        ref: 'tagsColumn',
        selector: 'addstudentswindow #tagsColumn'
    }, {
        ref: 'tagsAndExaminersColumn',
        selector: 'addstudentswindow #tagsAndExaminersColumn'
    }],

    init: function() {
        this.application.addListener({
            scope: this,
            managestudentsSuccessfullyLoaded: this._onManageStudentsLoaded
        });
        this.control({
            'viewport managestudentsoverview button[itemId=addstudents]': {
                click: this._onAddstudents
            },
            'addstudentswindow #saveButton': {
                click: this._onSave
            },
            'addstudentswindow #allowDuplicatesCheckbox': {
                change: this._onAllowDuplicatesChange,
                render: this._setTooltip
            },
            'addstudentswindow #includeTagsCheckbox': {
                change: this._onIncludeTagsChange,
                render: this._setTooltip
            },
            'addstudentswindow #automapExaminersCheckbox': {
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

    _onManageStudentsLoaded: function(manageStudentsController) {
        this.manageStudentsController = manageStudentsController;
        this._handleAddStudentsOnLoad();
    },

    _handleAddStudentsOnLoad: function() {
        var add_students_on_load = this.manageStudentsController.getOverview().add_students_on_load;
        console.log(add_students_on_load);
        if(add_students_on_load) {
            this._onAddstudents();
        }
    },

    _onAddstudents: function() {
        var relatedStudentsStore = this.getRelatedStudentsRoStore();
        relatedStudentsStore.loadWithAutomaticErrorHandling({
            scope: this,
            success: this._onLoadRelatedStudentsStoreSuccess,
            errortitle: gettext('Failed to load students from the period')
        });
    },

    _onLoadRelatedStudentsStoreSuccess: function(records) {
        var relatedExaminersStore = this.getRelatedExaminersRoStore();
        relatedExaminersStore.loadWithAutomaticErrorHandling({
            scope: this,
            success: this._onLoad,
            errortitle: gettext('Failed to load examiners from the period')
        });
    },

    _onLoad: function() {
        this.relatedExaminersMappedByTag = this.getRelatedExaminersRoStore().getMappedByTags();
        var relatedStudentsStore = this.getRelatedStudentsRoStore();
        relatedStudentsStore.clearFilter();

        this._filterOutRelatedStudentsAlreadyInGroup();
        relatedStudentsStore.sortBySpecialSorter('full_name');
        Ext.widget('addstudentswindow', {
            relatedStudentsStore: relatedStudentsStore,
            periodinfo: this.manageStudentsController.getPeriodInfo(),
            relatedExaminersMappedByTag: this.relatedExaminersMappedByTag
        }).show();
    },

    _filterOutRelatedStudentsAlreadyInGroup: function() {
        var relatedStudentsStore = this.getRelatedStudentsRoStore();
        var currentUsers = this.getGroupsStore().getGroupsMappedByUserId();
        relatedStudentsStore.filterBy(function(relatedStudentRecord) {
            var userid = relatedStudentRecord.get('user').id;
            return typeof currentUsers[userid] == 'undefined';
        });
    },

    _onAllowDuplicatesChange: function(field, allowDuplicates) {
        if(allowDuplicates) {
            this.getRelatedStudentsRoStore().clearFilter();
        } else {
            this._filterOutRelatedStudentsAlreadyInGroup();
        }
        this.getAddStudentsWindow().refreshBody();
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
        this.getAddStudentsWindow().close();
        this.manageStudentsController.notifyMultipleGroupsChange();
    }
});
