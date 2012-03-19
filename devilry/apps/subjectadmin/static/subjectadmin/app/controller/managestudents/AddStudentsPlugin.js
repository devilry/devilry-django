/**
 * Plugin for {@link subjectadmin.controller.managestudents.Overview} that
 * adds the ability to add students (groups with a single student) to an
 * assignment.
 *
 * Adds a _add students_ button to the list of groups toolbar.
 */
Ext.define('subjectadmin.controller.managestudents.AddStudentsPlugin', {
    extend: 'Ext.app.Controller',

    views: [
        'managestudents.AddStudentsWindow',
    ],

    stores: [
        'RelatedStudents',
        'RelatedExaminers',
        'Groups'
    ],

    refs: [{
        ref: 'window',
        selector: 'addstudentswindow'
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
            'addstudentswindow button[itemId=relatedLink]': {
                click: this._onRelatedLinkClick
            },
            'addstudentswindow savebutton': {
                click: this._onSave
            },
            'addstudentswindow cancelbutton': {
                click: this._onCancel
            },
        });
    },

    _onManageStudentsLoaded: function(manageStudentsController) {
        this.manageStudentsController = manageStudentsController;
        this.manageStudentsController.getPrimaryToolbar().insert(2, {
            xtype: 'button',
            itemId: 'addstudents',
            iconCls: 'icon-add-24',
            text: dtranslate('subjectadmin.managestudents.addstudents')
        });
        //this._onAddstudents();
    },

    _onRelatedLinkClick: function(ev) {
        console.log('_onRelatedLinkClick');
    },

    _onAddstudents: function() {
        var relatedStudentsStore = this.manageStudentsController.getRelatedStudentsStore();
        relatedStudentsStore.clearFilter();
        this._filterOutRelatedStudentsAlreadyInGroup(relatedStudentsStore);
        relatedStudentsStore.sort('user__devilryuserprofile__full_name', 'ASC');
        Ext.widget('addstudentswindow', {
            relatedStudentsStore: relatedStudentsStore,
            periodpath: Ext.String.format(
                '{0}.{1}',
                this.manageStudentsController.getSubjectShortname(),
                this.manageStudentsController.getPeriodShortname()
            )
        }).show();
    },

    _filterOutRelatedStudentsAlreadyInGroup: function(relatedStudentsStore) {
        var currentUsers = this.manageStudentsController.getGroupsMappedByUsername();
        relatedStudentsStore.filterBy(function(record) {
            var username = record.get('user__username');
            return currentUsers[username] === undefined;
        });
    },

    _onCancel: function(button) {
        this.getWindow().close();
    },

    _onSave: function(button) {
        console.log('save');
    }
});
