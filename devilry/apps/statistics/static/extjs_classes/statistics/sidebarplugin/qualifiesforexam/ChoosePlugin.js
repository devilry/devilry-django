Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.ChoosePlugin', {
    extend: 'Ext.form.ComboBox',

    config: {
        availablePlugins: [],
        commonArgs: undefined
    },

    constructor: function(config) {
        this.addEvents('pluginSelected');
        this.initConfig(config);
        this.callParent([config]);
    },


    initComponent: function() {
        var model = Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.ChoicesModel', {
            extend: 'Ext.data.Model',
            fields: ['label', 'path', 'args']
        });
        var store = Ext.create('Ext.data.Store', {
            model: model,
            data: this.availablePlugins
        });

        Ext.apply(this, {
            store: store,
            fieldLabel: 'How?',
            queryMode: 'local',
            displayField: 'label',
            valueField: 'path',
            emptyText: 'Please make a selection...',
            forceSelection: true,
        });
        this.on('select', this._onSelect, this);
        this.callParent(arguments);
    },

    _onSelect: function(field, values) {
        var record = values[0];
        var args = record.get('args');
        var label = record.get('label');
        var path = record.get('path');
        var config = {};
        Ext.apply(config, this.commonArgs);
        if(args) {
            Ext.apply(config, args);
        }
        var pluginObj = Ext.create(path, config);
        this.fireEvent('pluginSelected', pluginObj);
    }
});
