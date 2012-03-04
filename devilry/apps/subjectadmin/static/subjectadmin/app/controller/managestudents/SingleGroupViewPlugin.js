/**
 * Plugin for {@link subjectadmin.controller.managestudents.Overview} that
 * adds the ability to show information about and edit a single group when
 * it is selected.
 */
Ext.define('subjectadmin.controller.managestudents.SingleGroupViewPlugin', {
    extend: 'Ext.app.Controller',

    views: [
        'managestudents.SingleGroupView'
    ],

    init: function() {
        this.application.addListener({
            scope: this,
            managestudentsSingleGroupSelected: this._onSingleGroupSelected
        });
        this.control({
            'viewport singlegroupview': {
                render: this._onRender
            }
        });
    },

    _onSingleGroupSelected: function(manageStudentsController, groupRecord) {
        this.groupRecord = groupRecord;
        manageStudentsController.setBody({
            xtype: 'singlegroupview',
            groupRecord: groupRecord
        });
    },

    _onRender: function() {
        console.log('render');
    }
});
