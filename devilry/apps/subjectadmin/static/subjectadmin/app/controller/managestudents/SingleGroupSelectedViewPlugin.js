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

    models: [
        'Candidate'
    ],

    views: [
        'managestudents.SingleGroupSelectedView'
    ],

    //refs: [{
        //ref: '',
        //selector: 'singlegroupview'
    //}],

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
            topMessage: this._createTopMessage(),
            studentsStore: this._createStudentsStore(),
            groupRecord: groupRecord
        });
    },

    _createTopMessage: function() {
        var tpl = Ext.create('Ext.XTemplate', dtranslate('subjectadmin.managestudents.singlegroupselected.topmessage'));
        return tpl.apply({
            groupunit: this.manageStudentsController.getTranslatedGroupUnit()
        });
    },

    _onRender: function() {
        //console.log('render SingleGroupSelectedView');
    },

    _createStudentsStore: function() {
        console.log(this.groupRecord.get('students'));
        var store = Ext.create('Ext.data.Store', {
            model: this.getCandidateModel(),
            data: this.groupRecord.get('students')
        });
        return store;
    }
});
