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
        return interpolate(gettext('%(Students_term)s are is a group even when they work alone. No %(groups_term)s selected. Choose one or more %(groups_term)s to gain access to settings, such as %(examiners_term)s and %(tags_term)s.'), {
            Students_term: gettext('Students'),
            groups_term: gettext('groups'),
            examiners_term: gettext('examiners'),
            tags_term: gettext('tags')
        }, true);
    }
});
