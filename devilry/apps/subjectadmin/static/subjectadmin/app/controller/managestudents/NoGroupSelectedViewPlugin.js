/**
 * Plugin for {@link subjectadmin.controller.managestudents.Overview} that
 * adds the ability to show information when no group is selected.
 */
Ext.define('subjectadmin.controller.managestudents.NoGroupSelectedViewPlugin', {
    extend: 'Ext.app.Controller',

    views: [
        'managestudents.NoGroupSelectedView'
    ],

    init: function() {
        this.application.addListener({
            scope: this,
            managestudentsNoGroupSelected: this._onNoGroupSelected
        });
    },

    _onNoGroupSelected: function(manageStudentsController) {
        manageStudentsController.setBody({
            xtype: 'nogroupselectedview'
        });
    }
});
