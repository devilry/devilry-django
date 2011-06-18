{% load extjs %}

function comboBox()
{
    // Get the extjs model generated from the datamodel
    {{ RestStatConfig|extjs_model }}

    // Get the extjs store generated from the rest config
    var store = {{ RestStatConfig|extjs_store }}

    // Use them to create a simple combobox.
    var simpleCombo = Ext.create('Ext.form.field.ComboBox', {
        fieldLabel: 'Select statistics config',
        renderTo: 'simpleCombo',
        displayField: 'name',
        width: 400,
        labelWidth: 130,
        store: store,
        queryMode: 'local',
        typeAhead: true,
        listeners: {
            'select': on_select_combo
        }
    });



    // Period model and store (used in graph)
    {{ RestPeriod|extjs_model }}
    var periodstore = {{ RestPeriod|extjs_store }}

    var chart = null;

    // When selecting an item in the combobox
    function on_select_combo(field, value, options) {
        var data = value[0].data;
        var period_url = console.log(data.period_url);
        if(period_url) {
            console.log(period_url);
        }

        if(chart == null) {
            chart = Ext.create('Ext.chart.Chart', {
                width: 600,
                height: 400,
                store: periodstore,
                renderTo: 'graph',

                // Define axes
                axes: [{
                    type: 'Numeric',
                    position: 'bottom',
                    fields: ['id'],
                    title: 'Id',
                    minimum: 0
                }, {
                    type: 'Category',
                    position: 'left',
                    fields: ['long_name'],
                    title: 'Period'
                }],

                // Define series
                series: [{
                    type: 'bar',
                    axis: 'bottom',
                    xField: 'long_name',
                    yField: ['id']
                }]
            });
        }
    }

}


Ext.onReady(function() {
    comboBox();
});
