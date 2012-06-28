/**
 * Plugin for {@link devilry_subjectadmin.controller.managestudents.Overview} that
 * adds the ability to show information about and edit a multiple groups when
 * they are selected.
 */
Ext.define('devilry_subjectadmin.controller.managestudents.MultipleGroupsSelectedViewPlugin', {
    extend: 'Ext.app.Controller',

    views: [
        'managestudents.MultipleGroupsSelectedView'
    ],

    requires: [
        'devilry_extjsextras.AlertMessage'
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
        this.manageStudentsController = manageStudentsController;
        this.manageStudentsController.setBody({
            xtype: 'multiplegroupsview',
            multiselectHowto: this.manageStudentsController.getMultiSelectHowto(),
            topMessage: this._createTopMessage()
        });
    },

    _onRender: function() {
        //console.log('render MultipleGroupsSelectedView');
    },

    _createTopMessage: function() {
        var tpl = Ext.create('Ext.XTemplate', gettext('{numselected} {groupunit_plural} selected.'));
        return tpl.apply({
            numselected: this.groupRecords.length,
            groupunit_plural: this.manageStudentsController.getTranslatedGroupUnit(true)
        });
    },
});
