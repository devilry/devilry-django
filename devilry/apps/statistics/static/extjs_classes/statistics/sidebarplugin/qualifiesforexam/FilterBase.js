Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.FilterBase', {
    extend: 'Ext.container.Container',

    config: {
        loader: undefined,
        aggregatedStore: undefined,
        labelname: undefined,
        negative_labelname: undefined,
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
        this._loadSettings();
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
        if(!op.success) {
            this._handleLoadError('Save settings', op);
            return;
        }
        console.log(records);
        if(records.length === 0) {
            this.settingsRecord = Ext.create('devilry.apps.administrator.simplified.SimplifiedPeriodApplicationKeyValue', {
                period: this.loader.periodid,
                application: applicationid,
                key: 'settings',
                value: Ext.JSON.encode({
                    plugin: this.pluginname,
                    settings: this.getSettings()
                })
            });
        } else {
            this.settingsRecord = records[0];
        }
    },

    _onSave: function() {
        if(!this.validInput()) {
            return;
        }
        this._onSaveYes();
        return;
        Ext.MessageBox.show({
            title: 'Save?',
            msg: 'Are you sure you want to save? Students will be able to see if they are qualified for final exams.',
            buttons: Ext.Msg.YESNO,
            icon: Ext.Msg.QUESTION,
            closable: false,
            scope: this,
            fn: function(buttonId) {
                if(buttonId == 'yes') {
                    this._onSaveYes();
                }
            }
        });
    },

    _onSaveYes: function() {
        this._saveSettings();
    },

    _saveLabels: function() {
        this.loader.labelManager.setLabels({
            filter: this.filter,
            scope: this,
            label: this.labelname,
            negative_label: this.negative_labelname,
            student_can_read: true
        });
    },

    _saveSettings: function() {
        Ext.getBody().mask('Saving current settings', 'page-load-mask');
        this.settingsRecord.save({
            scope: this,
            callback: function(record, op) {
                Ext.getBody().unmask();
                if(!op.success) {
                    this._handleLoadError('Save settings', op);
                    return;
                }
                this._saveLabels();
            }
        });
    },

    _onPreview: function() {
        if(this.validInput()) {
            this.loader.clearFilter();
            this.loader.filterBy(this.title, this.filter, this);
        }
    },

    getSettings: function() {
        return false;
    },

    validInput: function() {
        return true;
    },


    _handleLoadError: function(details, op) {
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
