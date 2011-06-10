
function comboBox()
{
    // Get the extjs model generated from the datamodel
    {{ RestStatConfig.extjs_model_class|safe }}

    // Get the extjs store generated from the rest config
    var store = {{ RestStatConfig.get_extjs_store_object|safe }}

    // Use them to create a simple combobox.
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
