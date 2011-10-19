Ext.define('devilry.statistics.FilterEditor', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.statistics-filtereditor',
    requires: [
        'devilry.statistics.MustPassEditor',
        'devilry.statistics.PointSpecEditor'
    ],

    config: {
        assignment_store: undefined
    },

    constructor: function(config) {
        this.callParent([config]);
        this.initConfig(config);
    },

    initComponent: function() {
        Ext.apply(this, {
            items: [{
                xtype: 'box',
                html: 'Test'
            }, {
                xtype: 'tabpanel',
                items: [{
                    xtype: 'statistics-mustpasseditor',
                    title: 'Must pass',
                    assignment_store: this.assignment_store
                }, {
                    xtype: 'statistics-pointspeceditor',
                    title: 'Must have points',
                    assignment_store: this.assignment_store
                }]
            }],

            bbar: ['->', {
                xtype: 'button',
                text: 'Save label',
                iconCls: 'icon-save-32',
                scale: 'large'
            }]
        });
        this.callParent(arguments);
    }
});
