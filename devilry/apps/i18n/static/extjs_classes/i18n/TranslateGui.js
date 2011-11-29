Ext.define('devilry.i18n.TranslateGui', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.i18n-translategui',
    requires: [
        'devilry.i18n.TranslateGuiModel',
        'devilry.i18n.TranslateGuiGrid'
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
                store: this.store
            }],
        });
        this.callParent(arguments);
        this._loadDefaults();
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
    }
});
