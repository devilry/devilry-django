/**
 * Plugin for {@link devilry_subjectadmin.controller.managestudents.Overview} that
 * adds the ability to show information when no group is selected.
 */
Ext.define('devilry_subjectadmin.controller.managestudents.NoGroupSelectedViewPlugin', {
    extend: 'Ext.app.Controller',

    views: [
        'managestudents.NoGroupSelectedView'
    ],

    requires: [
        'devilry_extjsextras.AlertMessage'
    ],

    init: function() {
        this.application.addListener({
            scope: this,
            managestudentsNoGroupSelected: this._onNoGroupSelected
        });
    },

    _onNoGroupSelected: function(manageStudentsController) {
        this.manageStudentsController = manageStudentsController;
        this.manageStudentsController.setBodyCard('nogroupsSelected');
    }
});
