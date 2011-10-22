Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.FilterBase', {
    extend: 'Ext.container.Container',

    config: {
        loader: undefined,
        aggregatedStore: undefined,
        labelname: undefined,
        title: undefined
    },

    constructor: function(config) {
        this.saveButton = Ext.widget('button', {
            text: 'Save',
            iconCls: 'icon-save-32',
            scale: 'large',
            flex: 1,
            listeners: {
                scope: this,
                click: this._onSave
            }
        });
        this.previewButton = Ext.widget('button', {
            text: 'Show matching students',
            //iconCls: '',
            scale: 'large',
            flex: 1,
            listeners: {
                scope: this,
                click: this._onPreview
            }
        });

        this.defaultButtonPanel = Ext.widget('container', {
            items: [this.previewButton, this.saveButton],
            layout: {
                type: 'hbox',
                align: 'top'
            },
            height: 60
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
    },

    _onPreview: function() {
        this.loader.clearFilter();
        this.loader.filterBy(this.title, this.filter, this);
    }
});
