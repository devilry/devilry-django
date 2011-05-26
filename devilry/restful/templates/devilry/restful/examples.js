//Ext.require([
    //'Ext.grid.*',
    //'Ext.data.*',
    //'Ext.util.*',
    //'Ext.state.*',
    //'Ext.panel.*',
    //'Ext.layout.container.Border'
//]);




function comboBox()
{
    var states = [
        {"abbr":"AL","name":"Alabama","slogan":"The Heart of Dixie"},
        {"abbr":"AK","name":"Alaska","slogan":"The Land of the Midnight Sun"},
        {"abbr":"WI","name":"Wisconsin","slogan":"America's Dairyland"},
        {"abbr":"WY","name":"Wyoming","slogan":"Like No Place on Earth"}
    ];

    // Define the model for a State
    Ext.define('State', {
        extend: "Ext.data.Model",
        fields: [
            {type: 'string', name: 'abbr'},
            {type: 'string', name: 'name'},
            {type: 'string', name: 'slogan'}
        ]
    });

    // The data store holding the states
    var store = Ext.create('Ext.data.Store', {
        model: 'State',
        data: states
    });

    // Simple ComboBox using the data store
    var simpleCombo = Ext.create('Ext.form.field.ComboBox', {
        fieldLabel: 'Select a single state',
        renderTo: 'simpleCombo',
        displayField: 'name',
        width: 400,
        labelWidth: 130,
        store: store,
        queryMode: 'local',
        typeAhead: true
    });
}






function ajaxGrid()
{
    // create the grid

    var store = Ext.create('devilry.restful.store.Assignments');
    var grid = Ext.create('devilry.restful.view.assignments.List', {
        store: store,
        height: 300,
        width: 600,
        renderTo: 'grid-example',
        //columns: [
            //{header: 'Stuff', dataIndex: 'id', flex: 1},
            //{header: 'Name',  dataIndex: 'short_name',  flex: 1}]
    });
}






Ext.require('devilry.restful.view.assignments.List');
Ext.require('devilry.restful.model.Assignment');
Ext.require('devilry.restful.store.Assignments');
Ext.onReady(function(){
    //comboBox();
    ajaxGrid();
});

