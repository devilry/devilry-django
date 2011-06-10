
function comboBox()
{
    {{ RestStatConfig.extjs_model_class|safe }}
    var store = {{ RestStatConfig.get_extjs_store_object|safe }}
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
