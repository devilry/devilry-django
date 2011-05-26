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

    var grid = Ext.create('devilry.restful.view.assignments.Grid', {
        store: Ext.create('devilry.restful.store.Assignments', {
                    pageSize: 5,
                    longnamefields: 1
               }),
        height: 300,
        width: 600,
        renderTo: 'grid-example',
        //columns: [
            //{header: 'Stuff', dataIndex: 'id', flex: 1},
            //{header: 'Name',  dataIndex: 'short_name',  flex: 1}]
    });

    var simpleCombo = Ext.create('Ext.form.field.ComboBox', {
        fieldLabel: 'Select an assignment',
        renderTo: 'simpleCombo',
        displayField: 'path',
        width: 400,
        labelWidth: 130,
        store: Ext.create('devilry.restful.store.Assignments'),
        queryMode: 'local',
        typeAhead: true
    });


    var simpleCombo = Ext.create('Ext.form.field.ComboBox', {
        fieldLabel: 'Select an assignment',
        renderTo: 'fancyCombo',
        displayField: 'path',
        width: 400,
        labelWidth: 130,
        //store: Ext.create('devilry.restful.store.Assignments', {pageSize:10}),
        store: Ext.create('devilry.restful.store.Assignments'),
        queryMode: 'remote',
        typeAhead: true,
        hideLabel: true,
        minChars: 3,
        hideTrigger:true,

        listConfig: {
            loadingText: 'Searching...',

            // Custom rendering template for each item
            getInnerTpl: function() {
                return '<div class="fancyComboItem">' +
                    '<div class="comboMain">{long_name}</div>' +
                    '<div class="comboSmall">{path}</div>' +
                '</div>';
            }
        },
        //pageSize: 10,
    });
}




Ext.require('devilry.restful.view.assignments.Grid');
Ext.require('devilry.restful.model.Assignment');
Ext.require('devilry.restful.store.Assignments');
Ext.onReady(function(){
    //comboBox();
    ajaxGrid();
});

