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
        store: Ext.create('devilry.restful.store.Assignments'),
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
        displayField: 'short_name',
        width: 400,
        labelWidth: 130,
        store: Ext.create('devilry.restful.store.Assignments'),
        queryMode: 'local',
        typeAhead: true
    });


    var simpleCombo = Ext.create('Ext.form.field.ComboBox', {
        fieldLabel: 'Select an assignment',
        renderTo: 'fancyCombo',
        displayField: 'short_name',
        width: 400,
        labelWidth: 130,
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
                    '<div class="comboSmall">{parentnode__parentnode__short_name}.{parentnode__short_name}.{short_name}</div>' +
                '</div>';
            }
        },
        pageSize: 10,
    });


    //var panel = Ext.create('Ext.panel.Panel', {
        //renderTo: 'fancyCombo',
        //title: 'Search for an assignment',
        //width: 600,
        //bodyPadding: 10,
        //layout: 'anchor',

        //items: [{
            //xtype: 'combo',
            //store: store,
            //displayField: 'short_name',
            //typeAhead: false,
            //hideLabel: true,
            //hideTrigger:true,
            //anchor: '100%',

            //listConfig: {
                //loadingText: 'Searching...',
                //emptyText: 'No matching posts found.',

                //// Custom rendering template for each item
                //getInnerTpl: function() {
                    //return '<div class="fancyComboItem">' +
                        //'{parentnode__parentnode__short_name}.{parentnode__short_name}.{short_name}<br/>' +
                    //'</div>';
                //}
            //},
            //pageSize: 10,

            // override default onSelect to do redirect
            //listeners: {
                //select: function(combo, selection) {
                    //var post = selection[0];
                    //if (post) {
                        //window.location =
                            //Ext.String.format('http://www.sencha.com/forum/showthread.php?t={0}&p={1}', post.get('topicId'), post.get('id'));
                    //}
                //}
            //}
        //}, {
            //xtype: 'component',
            //style: 'margin-top:10px',
            //html: 'Live search requires a minimum of 4 characters.'
        //}]
    //});
}






Ext.require('devilry.restful.view.assignments.Grid');
Ext.require('devilry.restful.model.Assignment');
Ext.require('devilry.restful.store.Assignments');
Ext.onReady(function(){
    //comboBox();
    ajaxGrid();
});

