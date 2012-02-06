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
        ref: 'overview',
        selector: 'managestudentsoverview'
    }, {
        ref: 'addstudentsButton',
        selector: 'button[itemId=addstudents]'
    }],

    init: function() {
        this.application.addListener({
            scope: this,
            managestudentsSuccessfullyLoaded: this._onManageStudentsLoaded
        });
        this.control({
            'viewport managestudentsoverview button[itemId=addstudents]': {
                click: this._onAddstudents
            }
        });
    },

    _onManageStudentsLoaded: function(manageStudentsController) {
        this.manageStudentsController = manageStudentsController;
        this.manageStudentsController.getListofgroupsToolbar().add({
            xtype: 'button',
            itemId: 'addstudents',
            text: dtranslate('subjectadmin.managestudents.addstudents')
        });
    },

    _onAddstudents: function() {
        console.log('HEIi');
        //Ext.widget('addstudentswindow', {
            //store: this.manageStudentsController.getRelatedStudentsStore()
        //});
    }
});
