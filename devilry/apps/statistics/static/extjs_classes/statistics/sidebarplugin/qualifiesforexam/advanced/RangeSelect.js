Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.advanced.RangeSelect', {
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
        xtype: 'numberfield',
        emptyText: 'Example: 0'
    }, {
        name: "max",
        fieldLabel: "Maximum",
        xtype: 'numberfield',
        emptyText: 'Example: 1000'
    }]
});
