Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.advanced.gui.RangeSelect', {
    extend: 'Ext.form.Panel',
    alias: 'widget.statistics-rangeselect',

    config: {
        initialMin: undefined,
        initialMax: undefined
    },
    constructor: function(config) {
        this.callParent([config]);
        this.initConfig(config);
    },

    initComponent: function() {
        Ext.apply(this, {
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
                value: this.initialMin,
                emptyText: 'Example: 0. Not checked if not specified.'
            }, {
                name: "max",
                fieldLabel: "Maximum",
                xtype: 'numberfield',
                value: this.initialMax,
                emptyText: 'Example: 1000. Not checked if not specified.'
            }]
        });
        this.callParent(arguments);
    }
});
