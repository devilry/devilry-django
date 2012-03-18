/**
 * Plugin for {@link subjectadmin.controller.managestudents.Overview} that
 * adds the ability to show information when no group is selected.
 */
Ext.define('subjectadmin.controller.managestudents.NoGroupSelectedViewPlugin', {
    extend: 'Ext.app.Controller',

    views: [
        'managestudents.NoGroupSelectedView'
    ],

    requires: [
        'themebase.AlertMessage'
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
        var tpl = Ext.create('Ext.XTemplate', dtranslate('subjectadmin.managestudents.nogroupselected.topmessage'));
        return tpl.apply({
            groupunit_plural: this.manageStudentsController.getTranslatedGroupUnit(true)
        });
    },
});
