Ext.define('devilry.statistics.RangeSelect', {
    extend: 'Ext.form.Panel',
    alias: 'widget.statistics-rangeselect',

    layout: {
        type: 'vbox',
        align: 'stretch'
    },

    fieldDefaults: {
        labelAlign: 'top',
        labelWidth: 100,
        labelStyle: 'font-weight:bold'
    },

    items: [{
        name: "min",
        fieldLabel: "Minimum",
        xtype: 'textfield',
        emptyText: 'Example: 0'
    }, {
        name: "max",
        fieldLabel: "Maximum",
        xtype: 'textfield',
        emptyText: 'Example: 1000'
    }]
});
