Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.Main', {
    extend: 'Ext.form.Panel',
    title: 'Configure: Qualifies for final exam',
    requires: [
        'devilry.statistics.sidebarplugin.qualifiesforexam.ChoosePlugin',
        'devilry.statistics.sidebarplugin.qualifiesforexam.RequirePassingGradeOnAll',
        'devilry.statistics.sidebarplugin.qualifiesforexam.RequirePassingGradeOnSubset'
    ],
    config: {
        loader: undefined,
        aggregatedStore: undefined,
        labelname: 'qualifies-for-exam',
        sidebarplugins: []
    },

    bodyPadding: 10,

    layout: {
        type: 'vbox',
        align: 'stretch'
    },
    fieldDefaults: {
        labelAlign: 'top',
        labelWidth: 100,
        labelStyle: 'font-weight:bold'
    },
    defaults: {
        margins: '0 0 10 0'
    },

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },

    initComponent: function() {
        var chooseplugin = Ext.create('devilry.statistics.sidebarplugin.qualifiesforexam.ChoosePlugin', {
            availablePlugins: [{
                path: 'devilry.statistics.sidebarplugin.qualifiesforexam.RequirePassingGradeOnAll',
                label: 'Require passing grade on all assignments'
            }, {
                path: 'devilry.statistics.sidebarplugin.qualifiesforexam.RequirePassingGradeOnSubset',
                label: 'Require passing grade on a subset of all assignments'
            }],
            commonArgs: {
                loader: this.loader,
                aggregatedStore: this.aggregatedStore,
                labelname: this.labelname
            },

            listeners: {
                scope: this,
                pluginSelected: this._pluginSelected
            }
        });
        this._main = Ext.widget('container', {
            layout: 'fit'
        });
        Ext.apply(this, {
            items: [chooseplugin, this._main]
        });
        this.callParent(arguments);
    },

    _pluginSelected: function(pluginObj) {
        this._main.removeAll();
        //this._main.add({
            //xtype: 'box',
            //html: 'Hei'
        //});
        this._main.add(pluginObj);
    }
});
