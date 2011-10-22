Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.FilterBase', {
    extend: 'Ext.container.Container',

    config: {
        loader: undefined,
        aggregatedStore: undefined,
        labelname: undefined
    },

    constructor: function(config) {
        this.saveButton = Ext.widget('button', {
            text: 'Apply to all students',
            iconCls: 'icon-save-32',
            scale: 'large',
            listeners: {
                scope: this,
                click: this._onSave
            }
        });
        this.callParent([config]);
        this.initConfig(config);
    },

    _onSave: function() {
        this.loader.labelManager.setLabels({
            filter: this.filter,
            scope: this,
            label: this.labelname
        });
    }
});
