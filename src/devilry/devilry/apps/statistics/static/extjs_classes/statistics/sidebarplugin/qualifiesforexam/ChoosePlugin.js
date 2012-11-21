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
            fields: ['title', 'path', 'args'],
            idProperty: 'path'
        });
        var store = Ext.create('Ext.data.Store', {
            model: model,
            data: this.availablePlugins
        });

        Ext.apply(this, {
            store: store,
            fieldLabel: 'How?',
            queryMode: 'local',
            editable: false,
            displayField: 'title',
            valueField: 'path',
            emptyText: 'Please make a selection...',
            forceSelection: true
        });
        this.on('select', this._onSelect, this);
        this.callParent(arguments);
    },

    selectByPath: function(path) {
        var record = this.store.getById(path);
        this.select(record);
        this._onSelect(undefined, [record]);
    },

    _onSelect: function(field, values) {
        var record = values[0];
        var title = record.get('title');
        var path = record.get('path');
        var config = {title: title, path: path};
        Ext.apply(config, this.commonArgs);
        var pluginObj = Ext.create(path, config);
        this.fireEvent('pluginSelected', pluginObj);
    }
});
