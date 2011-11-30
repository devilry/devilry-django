Ext.define('devilry.i18n.TranslateGui', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.i18n-translategui',
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
            layout: 'fit',
            items: [{
                xtype: 'translategui-grid',
                store: this.store,
                listeners: {
                    scope: this,
                    itemdblclick: this._onDblClick
                }
            }],

            tbar: [{
                xtype: 'button',
                iconCls: 'icon-save-16',
                text: 'Save',
                listeners: {
                    scope: this,
                    click: this._onSave
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
        this._loadDefaults();
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
    },

    _onSave: function() {
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
                xtype: 'i18n-loadtranslationpanel'
            }
        }).show();
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
    }
});
