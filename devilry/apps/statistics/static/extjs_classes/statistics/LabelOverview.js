Ext.define('devilry.statistics.LabelOverview', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.statistics-labeloverview',

    layout: {
        type: 'hbox',
        align: 'stretch'
    },

    config: {
        labels: [],
        assignment_store: undefined
    },

    constructor: function(config) {
        this.callParent([config]);
        this.initConfig(config);
    },

    initComponent: function() {
        this.labelContainer = Ext.widget('panel', {
            title: 'Details',
            flex: 4,
            layout: 'accordion',
        });
        Ext.each(this.labels, function(label, index) {
            this._addLabel(label);
        }, this);
        Ext.apply(this, {
            items: [{
                xtype: 'box',
                flex: 6,
                html: 'Help'
            }, this.labelContainer],
            bbar: [{
                xtype: 'button',
                scale: 'large',
                iconCls: 'icon-add-32',
                text: 'Add label'
            }]
        });
        this.callParent(arguments);
    },

    _addLabel: function(label) {
        this.labelContainer.add({
            xtype: 'statistics-labelconfigeditor',
            assignment_store: this.assignment_store,
            label: label
        });
    }
});
