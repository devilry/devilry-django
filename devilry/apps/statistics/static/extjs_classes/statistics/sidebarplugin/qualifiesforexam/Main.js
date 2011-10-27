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
        'devilry.statistics.sidebarplugin.qualifiesforexam.Advanced',
        'devilry.statistics.sidebarplugin.qualifiesforexam.Manual',
        'devilry.statistics.sidebarplugin.qualifiesforexam.RequirePassingGradeOnSubset'
    ],
    config: {
        loader: undefined,
        aggregatedStore: undefined,
        labelname: 'qualifies-for-exam',
        negative_labelname: 'unqualified-for-exam',
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
        Ext.getBody().mask('Loading current settings', 'page-load-mask');
        this.initConfig(config);
        this.callParent([config]);
    },

    initComponent: function() {
        this.chooseplugin = Ext.create('devilry.statistics.sidebarplugin.qualifiesforexam.ChoosePlugin', {
            availablePlugins: [{
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
                title: 'No students qualify for final exams'
            }, {
                path: 'devilry.statistics.sidebarplugin.qualifiesforexam.All',
                title: 'All students qualify for final exams'
            }, {
                path: 'devilry.statistics.sidebarplugin.qualifiesforexam.Advanced',
                title: 'Advanced'
            }, {
                path: 'devilry.statistics.sidebarplugin.qualifiesforexam.Manual',
                title: 'Manually select the students that qualify for final exams'
            }],
            commonArgs: {
                loader: this.loader,
                aggregatedStore: this.aggregatedStore,
                labelname: this.labelname,
                negative_labelname: this.negative_labelname,
                main: this
            },

            listeners: {
                scope: this,
                pluginSelected: this._pluginSelected,
                render: this._onRenderChoices
            }
        });
        this._main = Ext.widget('container', {
            layout: 'fit'
        });
        Ext.apply(this, {
            items: [this.chooseplugin, this._main]
        });
        this.callParent(arguments);
    },

    _onRenderChoices: function() {
        this._loadSettings();
    },

    _pluginSelected: function(pluginObj) {
        this._main.removeAll();
        this.loader.clearFilter();
        this._main.add(pluginObj);
    },


    _loadSettings: function() {
        var applicationid = 'statistics-qualifiesforexam';
        this.relatedstudentkeyvalue_store = Ext.create('Ext.data.Store', {
            model: 'devilry.apps.administrator.simplified.SimplifiedPeriodApplicationKeyValue',
            remoteFilter: true,
            remoteSort: true
        });
        this.relatedstudentkeyvalue_store.pageSize = 1;
        this.relatedstudentkeyvalue_store.proxy.setDevilryFilters([{
            field: 'period',
            comp: 'exact',
            value: this.loader.periodid
        }, {
            field: 'application',
            comp: 'exact',
            value: applicationid
        }, {
            field: 'key',
            comp: 'exact',
            value: 'settings'
        }]);
        this.relatedstudentkeyvalue_store.load({
            scope: this,
            callback: this._onLoadSettings
        });
    },

    _onLoadSettings: function(records, op) {
        Ext.getBody().unmask();
        if(!op.success) {
            this._handleComError('Save settings', op);
            return;
        }
        if(records.length === 0) {
            this.settingsRecord = Ext.create('devilry.apps.administrator.simplified.SimplifiedPeriodApplicationKeyValue', {
                period: this.loader.periodid,
                application: applicationid,
                key: 'settings',
                value: null
            });
            this.settings = null;
        } else {
            this.settingsRecord = records[0];
            this.settings = Ext.JSON.decode(this.settingsRecord.get('value'));
            this.chooseplugin.selectByPath(this.settings.path);
        }
    },

    saveSettings: function(path, settings, callback, scope) {
        Ext.getBody().mask('Saving current settings', 'page-load-mask');
        var settingData = {
            path: path,
            settings: settings
        }
        this.settingsRecord.set('value', Ext.JSON.encode(settingData));
        this.settingsRecord.save({
            scope: this,
            callback: function(record, op) {
                Ext.getBody().unmask();
                if(!op.success) {
                    this._handleComError('Save settings', op);
                    return;
                }
                this.settings = settingData;
                Ext.bind(callback, scope)(op.success);
            }
        });
    },

    _handleComError: function(details, op) {
        // TODO: Make work for both model and store response
        Ext.getBody().unmask();
        var httperror = 'Lost connection with server';
        if(op.error.status !== 0) {
            httperror = Ext.String.format('{0} {1}', op.error.status, op.error.statusText);
        }
        Ext.MessageBox.show({
            title: 'Error',
            msg: '<p>This is usually caused by an unstable server connection. <strong>Try reloading the page</strong>.</p>' +
                Ext.String.format('<p>Error details: {0}: {1}</p>', httperror, details),
            buttons: Ext.Msg.OK,
            icon: Ext.Msg.ERROR,
            closable: false
        });
    }
});
