Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.Main', {
    extend: 'Ext.form.Panel',
    title: 'Label students that qualifies for final exams',
    requires: [
        'devilry.statistics.sidebarplugin.qualifiesforexam.ChoosePlugin',
        'devilry.statistics.sidebarplugin.qualifiesforexam.None',
        'devilry.statistics.sidebarplugin.qualifiesforexam.All',
        'devilry.statistics.sidebarplugin.qualifiesforexam.RequirePointsOnAll',
        'devilry.statistics.sidebarplugin.qualifiesforexam.RequirePointsOnSubset',
        'devilry.statistics.sidebarplugin.qualifiesforexam.RequirePassingGradeOnAll',
        'devilry.statistics.sidebarplugin.qualifiesforexam.Manual',
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
                path: 'devilry.statistics.sidebarplugin.qualifiesforexam.None',
                title: 'No students qualify for final exams'
            }, {
                path: 'devilry.statistics.sidebarplugin.qualifiesforexam.All',
                title: 'All students qualify for final exams'
            }, {
                path: 'devilry.statistics.sidebarplugin.qualifiesforexam.RequirePassingGradeOnAll',
                title: 'Require passing grade on all assignments'
            }, {
                path: 'devilry.statistics.sidebarplugin.qualifiesforexam.RequirePassingGradeOnSubset',
                title: 'Require passing grade on a subset of all assignments'
            }, {
                path: 'devilry.statistics.sidebarplugin.qualifiesforexam.RequirePointsOnAll',
                title: 'Require a minimum number of points in total on all assignments'
            }, {
                path: 'devilry.statistics.sidebarplugin.qualifiesforexam.RequirePointsOnSubset',
                title: 'Require a minimum number of points in total on a subset of all assignments'
            }, {
                path: 'devilry.statistics.sidebarplugin.qualifiesforexam.None',
                title: 'Advanced'
            }, {
                path: 'devilry.statistics.sidebarplugin.qualifiesforexam.Manual',
                title: 'Manually select the students that qualify for final exams'
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
        this.loader.clearFilter();
        this._main.add(pluginObj);
    }
});
