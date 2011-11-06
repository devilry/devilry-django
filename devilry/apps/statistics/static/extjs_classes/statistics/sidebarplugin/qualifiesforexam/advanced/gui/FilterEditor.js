Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.advanced.gui.FilterEditor', {
    extend: 'Ext.tab.Panel',
    alias: 'widget.statistics-filtereditor',
    requires: [
        'devilry.statistics.sidebarplugin.qualifiesforexam.advanced.gui.MustPassEditor',
        'devilry.statistics.sidebarplugin.qualifiesforexam.advanced.gui.PointSpecEditor'
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
                xtype: 'statistics-mustpasseditor',
                title: 'Must pass',
                assignment_store: this.assignment_store
            }, {
                xtype: 'statistics-pointspeceditor',
                title: 'Must have points',
                assignment_store: this.assignment_store
            }],

            bbar: ['->', {
                xtype: 'button',
                text: 'Add filter',
                iconCls: 'icon-add-32',
                scale: 'large',
                listeners: {
                    scope: this,
                    click: this._onAdd
                }
            }]
        });
        this.callParent(arguments);
    },

    getFilterArgs: function() {
        var must_pass = this.down('statistics-mustpasseditor').getResult();
        try {
            var pointspec = this.down('statistics-pointspeceditor').getResult();
        } catch(e) {
            this.down('statistics-pointspeceditor').show();
            Ext.MessageBox.alert('Error', e);
            return false;
        }
        return {
            must_pass: must_pass,
            pointspecArgs: pointspec
        };
    },

    _onAdd: function() {
        var filterArgs = this.getFilterArgs();
        if(filterArgs != false) {
            this.fireEvent('addFilter', filterArgs);
        }
    }
});
