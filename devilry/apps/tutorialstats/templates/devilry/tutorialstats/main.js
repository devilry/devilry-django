//Ext.require('devilry.restful.view.assignments.Grid');
//Ext.require('devilry.restful.PathRestProxy');
//Ext.require('devilry.restful.store.SubjectTree');
Ext.require('devilry.tutorialstats.store.StatConfig');


function comboBox()
{
    var simpleCombo = Ext.create('Ext.form.field.ComboBox', {
        fieldLabel: 'Select statistics config',
        renderTo: 'simpleCombo',
        displayField: 'name',
        width: 400,
        labelWidth: 130,
        store: Ext.create('devilry.tutorialstats.store.StatConfig'),
        queryMode: 'local',
        typeAhead: true
    });
}


Ext.onReady(function() {
    comboBox();
});
