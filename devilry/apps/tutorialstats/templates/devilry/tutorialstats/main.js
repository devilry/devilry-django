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





    Ext.define('restperiodpoints', {
        extend: 'Ext.data.Model',
        fields: [
            {"type": "string", "name": "username"},
            {"type": "int", "name": "sumperiod"}],
        idProperty: 'username'
    });
    


    var chart = null;

    // When selecting an item in the combobox
    function on_select_combo(field, value, options) {
        var data = value[0].data;
        var periodpoints_url = data.periodpoints_url;
        if(periodpoints_url) {
            //console.log(periodpoints_url);
            var restperiodpoints_store = Ext.create('Ext.data.Store', {
                model: 'restperiodpoints',
                autoLoad: true,
                autoSync: true,
                proxy: {
                    type: 'rest',
                    url: periodpoints_url,
                    reader: {
                        type: 'json',
                        root: 'items'
                    }
                }
            });

            if(chart) {
                chart.bindStore(restperiodpoints_store);
            } else {
                chart = Ext.create('Ext.chart.Chart', {
                    width: 600,
                    height: 400,
                    store: restperiodpoints_store,
                    renderTo: 'graph',

                    // Define axes
                    axes: [{
                        type: 'Numeric',
                        position: 'bottom',
                        fields: ['sumperiod'],
                        title: 'Points this period',
                        minimum: 0
                    }, {
                        type: 'Category',
                        position: 'left',
                        fields: ['username'],
                        title: 'Student'
                    }],

                    // Define series
                    series: [{
                        type: 'bar',
                        axis: 'bottom',
                        xField: 'username',
                        yField: ['sumperiod']
                    }]
                });
            }
        }
    }

}


Ext.onReady(function() {
    comboBox();
});
