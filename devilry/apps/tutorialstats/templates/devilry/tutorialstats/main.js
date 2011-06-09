
function comboBox()
{
    Ext.define('StatConfig', {
        extend: 'Ext.data.Model',
        fields: [
            {name:'id', type:'int'},
            {name:'name', type:'string'},
            {name:'period__id', type:'int'},
            {name:'user__id', type:'int'}
        ],
        idProperty: 'id'
    });

    var store = Ext.create('Ext.data.Store', {
        model: 'StatConfig',
        autoLoad: true,
        autoSync: true,
        proxy: {
            type: 'rest',
            url: '/tutorialstats/rest/',
            reader: {
                type: 'json',
                root: 'items'
            },
            writer: 'json'
        }
    });

    var simpleCombo = Ext.create('Ext.form.field.ComboBox', {
        fieldLabel: 'Select statistics config',
        renderTo: 'simpleCombo',
        displayField: 'name',
        width: 400,
        labelWidth: 130,
        store: store,
        queryMode: 'local',
        typeAhead: true
    });
}


Ext.onReady(function() {
    comboBox();
});
