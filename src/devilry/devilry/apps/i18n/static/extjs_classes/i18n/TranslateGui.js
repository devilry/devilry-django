Ext.define('devilry.i18n.TranslateGui', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.i18n-translategui',
    title: 'Translate Devilry',
    bodyPadding: 5,
    requires: [
        'devilry.i18n.MemoryStorageProxyWithExtraEvents',
        'devilry.i18n.TranslateGuiModel',
        'devilry.i18n.TranslateGuiGrid',
        'devilry.jsfiledownload.JsFileDownload',
        'devilry.i18n.LoadTranslationPanel',
        'devilry.i18n.EditRecordForm'
    ],

    localStorageKey: 'devilry-i18n-translategui',

    initComponent: function() {
        if (typeof(localStorage) == 'undefined' ) {
            alert('Your browser does not support HTML5 localStorage. Try upgrading.');
            return;
        }
        this.translationspath = Ext.String.format('{0}/i18n/translations', DevilrySettings.DEVILRY_STATIC_URL);
        this.store = Ext.create('Ext.data.Store', {
            model: 'devilry.i18n.TranslateGuiModel',
            autoSync: true,
            proxy: Ext.create('devilry.i18n.MemoryStorageProxyWithExtraEvents'),
            listeners: {
                scope: this,
                datachanged: this._onDataChanged
            }
        });
        Ext.apply(this, {
            layout: 'border',
            items: {
                xtype: 'translategui-grid',
                store: this.store,
                region: 'center',
                autoScroll: true,
                listeners: {
                    scope: this,
                    itemdblclick: this._onDblClick
                }
            },

            listeners: {
                scope: this,
                render: function() {
                    this._loadDefaults();
                }
            },

            tbar: [{
                xtype: 'button',
                iconCls: 'icon-save-16',
                text: 'Export',
                listeners: {
                    scope: this,
                    click: this._onExport
                }
            }, {
                xtype: 'button',
                text: 'Load',
                listeners: {
                    scope: this,
                    click: this._onLoad
                }
            }, {
                xtype: 'button',
                text: 'New',
                listeners: {
                    scope: this,
                    click: this._onNew
                }
            }]
        });
        this.callParent(arguments);
    },

    _onNew: function() {
        this._clear();
        this._addDefaultsToStore();
    },

    _clear: function() {
        this.store.removeAll();
        localStorage.removeItem(this.localStorageKey);
    },

    _onDataChanged: function() {
        localStorage.setItem(this.localStorageKey, this._exportJson());
    },

    _loadFromLocalStorage: function() {
        if('localStorage' in window && window['localStorage'] !== null) {
            
        } else {
            //localStorage.setItem("name", "Hello World!");
            alert("Your browser does not support HTML5 localStorage. Try upgrading.");
        }
    },

    _onDblClick: function(view, record) {
        Ext.widget('window', {
            modal: true,
            title: 'Edit - ' + record.get('key'),
            width: 600,
            height: 400,
            layout: {
                type: 'hbox',
                align: 'stretch'
            },
            items: [{
                xtype: 'panel',
                title: 'Default value',
                bodyPadding: 5,
                flex: 1,
                html: record.get('defaultvalue')
            }, {
                xtype: 'i18n-editrecordform',
                record: record
            }]
        }).show();
    },

    _onRequiredFilesLoaded: function() {
        localData = localStorage.getItem(this.localStorageKey);
        if(localData !== null) {
            this._loadExistingTranslation(localData);
        }
    },

    _loadDefaults: function() {
        this.getEl().mask('Loading...');
        Ext.Ajax.request({
            url: Ext.String.format('{0}/messages.json', this.translationspath),
            scope: this,
            success: this._onLoadDefaults
        });
    },

    _onLoadDefaults: function(response) {
        this.defaults = Ext.JSON.decode(response.responseText);
        this._loadIndex();
    },

    _addDefaultsToStore: function() {
        this.store.suspendEvents();
        Ext.Object.each(this.defaults, function(key, value) {
            this.store.add({
                key: key,
                defaultvalue: value
            });
        }, this);
        this.store.resumeEvents();
        this.store.fireEvent('datachanged');
    },

    _onExport: function() {
        var result = this._exportJson();
        devilry.jsfiledownload.JsFileDownload.saveas('devilry-translation.json', result);
    },

    _onLoad: function() {
        Ext.widget('window', {
            modal: true,
            title: 'Load translation',
            width: 600,
            height: 400,
            layout: 'fit',
            items: {
                xtype: 'i18n-loadtranslationpanel',
                index: this.index,
                translationspath: this.translationspath,
                listeners: {
                    scope: this,
                    exportdataLoaded: this._loadExistingTranslation
                }
            }
        }).show();
    },

    _loadExistingTranslation: function(jsondata) {
        this._clear();
        this._addDefaultsToStore();
        var translation = Ext.JSON.decode(jsondata);
        this.store.suspendEvents();
        Ext.each(this.store.data.items, function(record, index) {
            record.set('translation', '');
            record.commit();
        });
        Ext.Object.each(translation, function(key, value) {
            var record = this.store.getById(key);
            record.set('translation', value);
            record.commit();
        }, this);
        this.store.resumeEvents();
        this.store.fireEvent('datachanged');
    },

    _exportJson: function() {
        var result = new Object();
        Ext.each(this.store.data.items, function(record, index) {
            var translation = Ext.String.trim(record.get('translation'));
            if(translation) {
                var key = record.get('key');
                result[key] = translation;
            }
        }, this);
        return Ext.JSON.encode(result);
    },

    _loadIndex: function() {
        Ext.Ajax.request({
            url: Ext.String.format('{0}/index.json', this.translationspath),
            scope: this,
            success: function(response) {
                this.index = Ext.JSON.decode(response.responseText);
                this.getEl().unmask();
                this._onRequiredFilesLoaded();
            }
        });
    }
});
