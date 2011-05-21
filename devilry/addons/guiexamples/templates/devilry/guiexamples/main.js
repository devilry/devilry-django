var states = [
{"abbr":"AL","name":"Alabama","slogan":"The Heart of Dixie"},
{"abbr":"AK","name":"Alaska","slogan":"The Land of the Midnight Sun"},
{"abbr":"WI","name":"Wisconsin","slogan":"America's Dairyland"},
{"abbr":"WY","name":"Wyoming","slogan":"Like No Place on Earth"}
];



Ext.onReady(function(){
    console.info('woohoo again!!!');
    
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
}); //end onReady

