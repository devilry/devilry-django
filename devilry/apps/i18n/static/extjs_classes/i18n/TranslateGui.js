Ext.define('devilry.i18n.TranslateGui', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.i18n-translategui',
    title: 'Translate Devilry',
    bodyPadding: 5,
    requires: [
        'devilry.i18n.TranslateGuiModel',
        'devilry.i18n.TranslateGuiGrid',
        'devilry.jsfiledownload.JsFileDownload',
        'devilry.i18n.LoadTranslationPanel',
        'devilry.i18n.EditRecordForm'
    ],

    initComponent: function() {
        this.store = Ext.create('Ext.data.Store', {
            model: 'devilry.i18n.TranslateGuiModel',
            autoSync: false,
            proxy: 'memory'
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
                    this.getEl().mask('Loading...');
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
            }]
        });
        this.callParent(arguments);
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

    _loadDefaults: function() {
        Ext.Ajax.request({
            url: Ext.String.format('{0}/i18n/messages.json', DevilrySettings.DEVILRY_STATIC_URL),
            scope: this,
            success: this._onLoadDefaults
        });
    },

    _onLoadDefaults: function(response) {
        var defaults = Ext.JSON.decode(response.responseText);
        Ext.Object.each(defaults, function(key, value) {
            this.store.add({
                key: key,
                defaultvalue: value
            });
        }, this);
        this._loadIndex();
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
                listeners: {
                    scope: this,
                    exportdataLoaded: this._loadExistingTranslation
                }
            }
        }).show();
    },

    _loadExistingTranslation: function(jsondata) {
        var translation = Ext.JSON.decode(jsondata);
        Ext.each(this.store.data.items, function(record, index) {
            record.set('translation', '');
            record.commit();
        });
        Ext.Object.each(translation, function(key, value) {
            var record = this.store.getById(key);
            record.set('translation', value);
            record.commit();
        }, this);
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
            url: Ext.String.format('{0}/i18n/index.json', DevilrySettings.DEVILRY_STATIC_URL),
            scope: this,
            success: function(response) {
                this.index = Ext.JSON.decode(response.responseText);
                this.getEl().unmask();
            }
        });
    }
});
