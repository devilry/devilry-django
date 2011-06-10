
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


    window.generateData = function(n, floor) {
        var data = [],
            p = (Math.random() * 11) + 1,
            i;

        floor = (!floor && floor !== 0) ? 20 : floor;

        for (i = 0; i < (n || 12); i++) {
            data.push({
                name: Ext.Date.monthNames[i % 12],
                data1: Math.floor(Math.max((Math.random() * 100), floor)),
            });
        }
        return data;
    };


    var chartstore = Ext.create('Ext.data.JsonStore', {
        fields: ['name', 'data1'],
        data: generateData()
    });


    var chart = Ext.create('Ext.chart.Chart', {
        width: 200,
        height: 200,
        store: chartstore,

        // Define axes
        axes: [{
            type: 'Numeric',
            position: 'bottom',
            fields: ['data1'],
            title: 'Number of Hits',
            minimum: 0
        }, {
            type: 'Category',
            position: 'left',
            fields: ['name'],
            title: 'Month of the Year'
        }],

        // Define series
        series: [{
            type: 'bar',
            axis: 'bottom',
            xField: 'name',
            yField: ['data1']
        }]
    });

    var win = Ext.create('Ext.Window', {
        width: 800,
        height: 600,
        hidden: false,
        maximizable: true,
        title: 'Bar Chart',
        renderTo: Ext.getBody(),
        layout: 'fit',
        items: [chart]
    });
}


Ext.onReady(function() {
    comboBox();
});
