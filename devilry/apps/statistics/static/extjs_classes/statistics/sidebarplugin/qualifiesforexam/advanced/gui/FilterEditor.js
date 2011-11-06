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
                text: 'Save filter',
                iconCls: 'icon-save-32',
                scale: 'large',
                listeners: {
                    scope: this,
                    click: this._onSave
                }
            }]
        });
        this.callParent(arguments);
    },

    getFilter: function() {
        var must_pass = this.down('statistics-mustpasseditor').getResult();
        try {
            var pointspec = this.down('statistics-pointspeceditor').getResult();
        } catch(e) {
            this.down('statistics-pointspeceditor').show();
            Ext.MessageBox.alert('Error', e);
        }
        return Ext.create('devilry.statistics.sidebarplugin.qualifiesforexam.advanced.Filter', {
            must_pass: must_pass,
            pointspec: pointspec
        });
    },

    _onSave: function() {
        this.fireEvent('save', this.getFilter());
    }
});
