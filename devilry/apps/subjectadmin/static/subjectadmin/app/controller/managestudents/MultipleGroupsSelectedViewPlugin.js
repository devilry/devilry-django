/**
 * Plugin for {@link subjectadmin.controller.managestudents.Overview} that
 * adds the ability to show information about and edit a multiple groups when
 * they are selected.
 */
Ext.define('subjectadmin.controller.managestudents.MultipleGroupsSelectedViewPlugin', {
    extend: 'Ext.app.Controller',

    views: [
        'managestudents.MultipleGroupsSelectedView'
    ],

    init: function() {
        this.application.addListener({
            scope: this,
            managestudentsMultipleGroupsSelected: this._onMultipleGroupsSelected
        });
        this.control({
            'viewport multiplegroupsview': {
                render: this._onRender
            }
        });
    },

    _onMultipleGroupsSelected: function(manageStudentsController, groupRecords) {
        this.groupRecords = groupRecords;
        manageStudentsController.setBody({
            xtype: 'multiplegroupsview',
            groupRecords: groupRecords
        });
    },

    _onRender: function() {
        console.log('render MultipleGroupsSelectedView');
    }
});
