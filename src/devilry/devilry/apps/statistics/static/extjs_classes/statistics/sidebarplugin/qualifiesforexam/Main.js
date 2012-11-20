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
        'devilry.statistics.sidebarplugin.qualifiesforexam.RequirePassingGradeOnSubset',
        'devilry.extjshelpers.DateTime'
    ],
    config: {
        loader: undefined,
        aggregatedStore: undefined,
        labelname: 'qualifies-for-exam',
        negative_labelname: 'unqualified-for-exam',
        sidebarplugins: []
    },
    applicationid: 'statistics-qualifiesforexam',

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
        margin: '0 0 10 0'
    },

    constructor: function(config) {
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
            flex: 1,
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
        this._mask('Loading current settings', 'page-load-mask');
        this.periodapplicationkeyvalue_store = Ext.create('Ext.data.Store', {
            model: 'devilry.apps.administrator.simplified.SimplifiedPeriodApplicationKeyValue',
            remoteFilter: true,
            remoteSort: true
        });
        this.periodapplicationkeyvalue_store.proxy.setDevilryFilters([{
            field: 'period',
            comp: 'exact',
            value: this.loader.periodid
        }, {
            field: 'application',
            comp: 'exact',
            value: this.applicationid
        //}, {
            //field: 'key',
            //comp: 'exact',
            //value: 'settings'
        }]);
        this.periodapplicationkeyvalue_store.proxy.setDevilryOrderby(['-key']);
        this.periodapplicationkeyvalue_store.pageSize = 2; // settings and ready-for-export
        this.periodapplicationkeyvalue_store.load({
            scope: this,
            callback: this._onLoadSettings
        });
    },

    _onLoadSettings: function(records, op) {
        this._unmask();
        if(!op.success) {
            this._handleComError('Save settings', op);
            return;
        }

        var settingsindex = this.periodapplicationkeyvalue_store.findExact('key', 'settings');
        if(settingsindex > -1) {
            this.settingsRecord = records[settingsindex];
            this.settings = Ext.JSON.decode(this.settingsRecord.get('value'));
            this.chooseplugin.selectByPath(this.settings.path);
        } else {
            this.settingsRecord = Ext.create('devilry.apps.administrator.simplified.SimplifiedPeriodApplicationKeyValue', {
                period: this.loader.periodid,
                application: this.applicationid,
                key: 'settings',
                value: null
            });
        }

        var readyForExportIndex = this.periodapplicationkeyvalue_store.findExact('key', 'ready-for-export');
        if(readyForExportIndex > -1) {
            this.readyForExportRecord = records[readyForExportIndex];
        } else {
            this.readyForExportRecord = Ext.create('devilry.apps.administrator.simplified.SimplifiedPeriodApplicationKeyValue', {
                period: this.loader.periodid,
                application: this.applicationid,
                key: 'ready-for-export',
                value: null
            });
        }
    },

    saveSettings: function(path, settings, callback, scope) {
        this._mask('Saving current settings', 'page-load-mask');
        var settingData = {
            path: path,
            settings: settings
        };
        this.settingsRecord.set('value', Ext.JSON.encode(settingData));
        this.settingsRecord.save({
            scope: this,
            callback: function(record, op) {
                this._unmask();
                if(!op.success) {
                    this._handleComError('Save settings', op);
                    return;
                }
                this.settings = settingData;
                this._saveReadyForExportRecord(callback, scope);
            }
        });
    },

    _saveReadyForExportRecord: function(callback, scope) {
        this._mask('Marking as ready for export', 'page-load-mask');
        this.readyForExportRecord.set('value', Ext.JSON.encode({
            isready: 'yes',
            savetime: devilry.extjshelpers.DateTime.restfulNow()
        }));
        this.readyForExportRecord.save({
            scope: this,
            callback: function(record, op) {
                this._unmask();
                if(!op.success) {
                    this._handleComError('Mark ready for export', op);
                    return;
                }
                Ext.bind(callback, scope)();
            }
        });
    },

    _handleComError: function(details, op) {
        this._unmask();
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
    },

    _mask: function(msg) {
        this.getEl().mask(msg);
    },

    _unmask: function() {
        this.getEl().unmask();
    }
});
