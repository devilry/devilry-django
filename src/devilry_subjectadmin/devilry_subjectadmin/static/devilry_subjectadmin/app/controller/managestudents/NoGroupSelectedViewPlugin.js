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
        this.manageStudentsController.setBody({
            xtype: 'nogroupselectedview',
            topMessage: this._createTopMessage()
        });
    },

    _createTopMessage: function() {
        var tpl = Ext.create('Ext.XTemplate', gettext('No {groupunit_plural} selected. Choose one or more {groupunit_plural} to gain access to settings, such as examiners and tags.'));
        return tpl.apply({
            groupunit_plural: this.manageStudentsController.getTranslatedGroupUnit(true)
        });
    },
});
