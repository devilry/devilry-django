Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.advanced.gui.FilterEditor', {
    extend: 'Ext.tab.Panel',
    alias: 'widget.statistics-filtereditor',
    requires: [
        'devilry.statistics.sidebarplugin.qualifiesforexam.advanced.gui.MustPassEditor',
        'devilry.statistics.sidebarplugin.qualifiesforexam.advanced.gui.PointSpecEditor'
    ],

    config: {
        assignment_store: undefined,
        filterRecord: undefined
    },

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },

    initComponent: function() {
        var filter;
        if(this.filterRecord) {
            filter = this.filterRecord.get('filter');
        }
        Ext.apply(this, {
            items: [{
                xtype: 'statistics-mustpasseditor',
                title: 'Must pass',
                must_pass: filter? filter.must_pass: undefined,
                assignment_store: this.assignment_store
            }, {
                xtype: 'statistics-pointspeceditor',
                title: 'Must have points',
                pointspec: filter? filter.pointspec: undefined,
                assignment_store: this.assignment_store
            }],

            bbar: ['->', {
                xtype: 'button',
                text: this.filterRecord? 'Update rule': 'Add rule',
                iconCls: this.filterRecord? 'icon-save-32': 'icon-add-32',
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
        var pointspec;
        try {
            pointspec = this.down('statistics-pointspeceditor').getResult();
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
        if(filterArgs !== false) {
            this.fireEvent('addFilter', filterArgs, this.filterRecord);
        }
    }
});
