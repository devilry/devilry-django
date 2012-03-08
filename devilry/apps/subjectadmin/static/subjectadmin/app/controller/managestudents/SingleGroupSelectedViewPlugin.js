/**
 * Plugin for {@link subjectadmin.controller.managestudents.Overview} that
 * adds the ability to show information about and edit a single group when
 * it is selected.
 */
Ext.define('subjectadmin.controller.managestudents.SingleGroupSelectedViewPlugin', {
    extend: 'Ext.app.Controller',

    requires: [
        'themebase.AlertMessage'
    ],

    views: [
        'managestudents.SingleGroupSelectedView'
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
        this.manageStudentsController = manageStudentsController;
        this.groupRecord = groupRecord;
        this.manageStudentsController.setBody({
            xtype: 'singlegroupview',
            multiselectHowto: this.manageStudentsController.getMultiSelectHowto(),
            topMessage: this._createTopMessage()
        });
    },

    _createTopMessage: function() {
        var tpl = Ext.create('Ext.XTemplate', dtranslate('subjectadmin.managestudents.singlegroupselected.topmessage'));
        return tpl.apply({
            groupunit: this.manageStudentsController.getTranslatedGroupUnit()
        });
    },

    _onRender: function() {
        console.log(this.groupRecord);
        //console.log('render SingleGroupSelectedView');
    }
});
