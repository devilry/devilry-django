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
        'Groups'
    ],

    refs: [{
        ref: 'addStudentsWindow',
        selector: 'addstudentswindow'
    }, {
        ref: 'selectedStudentsGrid',
        selector: 'addstudentswindow grid'
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
                change: this._onAllowDuplicatesChange
            }
        });
    },

    _onManageStudentsLoaded: function(manageStudentsController) {
        this.manageStudentsController = manageStudentsController;
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
        var relatedStudentsStore = this.getRelatedStudentsRoStore();
        relatedStudentsStore.clearFilter();

        this._filterOutRelatedStudentsAlreadyInGroup();
        relatedStudentsStore.sortBySpecialSorter('full_name');
        Ext.widget('addstudentswindow', {
            relatedStudentsStore: relatedStudentsStore,
            periodinfo: this.manageStudentsController.getPeriodInfo()
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

    _onSave: function(button) {
        var selModel = this.getSelectedStudentsGrid().getSelectionModel();
        var selectedRelatedStudents = selModel.getSelection();
        var groupsStore = this.getGroupsStore();
        var includeTags = true;
        Ext.Array.each(selectedRelatedStudents, function(relatedStudentRecord) {
            var groupRecord = groupsStore.addFromRelatedStudentRecord({
                relatedStudentRecord: relatedStudentRecord,
                includeTags: includeTags
            });
        }, this);
        this.getAddStudentsWindow().close();
        this.manageStudentsController.notifyMultipleGroupsChange();
    }
});
