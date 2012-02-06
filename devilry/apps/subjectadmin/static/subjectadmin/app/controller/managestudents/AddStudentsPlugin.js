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

            'addstudentswindow': {
                render: this._onRenderWindow
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
        this.manageStudentsController.getListofgroupsToolbar().add({
            xtype: 'button',
            itemId: 'addstudents',
            text: dtranslate('subjectadmin.managestudents.addstudents')
        });
        this._onAddstudents();
    },

    _onRenderWindow: function() {
        var windowEl = this.getWindow().getEl();
        Ext.defer(function() {
            var relatedlink = windowEl.query('.relatedlink')[0];
            var relatedlinkEl = Ext.create('Ext.Element', relatedlink);
            relatedlinkEl.on('click', this._onRelatedLinkClick, this);
        }, 200, this);
    },

    _onRelatedLinkClick: function(ev) {
        console.log('hei');
        ev.stopEvent();
    },

    _onAddstudents: function() {
        var relatedStudentsStore = this.manageStudentsController.getRelatedStudentsStore();
        relatedStudentsStore.clearFilter();
        this._filterOutRelatedStudentsAlreadyInGroup(relatedStudentsStore);
        relatedStudentsStore.sort('user__devilryuserprofile__full_name', 'ASC');
        console.log(relatedStudentsStore.data.items[0]);
        Ext.widget('addstudentswindow', {
            relatedStudentsStore: relatedStudentsStore
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
