Ext.define('devilry_i18n.LanguageSelectWidget', {
    extend: 'Ext.container.Container',
    alias: 'widget.devilry_i18n_languageselect',
    cls: 'devilry_i18n_languageselect',


    /**
     * @cfg {bool} [hideLabel]
     * Forwarded to the interal combobox.
     */

    /**
     * @cfg {bool} [fieldLabel]
     * Forwarded to the interal combobox.
     */

    requires: [
        'Ext.window.MessageBox',
        'Ext.data.Store',
        'devilry_i18n.LanguageSelectModel'
    ],

    initComponent: function() {
        this.loadTries = 0;
        Ext.apply(this, {
            layout: 'fit',
            items: [{
                xtype: 'box',
                html: gettext('Loading') + ' ...'
            }]
        });
        this.callParent(arguments);
        this._loadLanguages();
    },

    _createAvailableLanguagesStore: function(availableLanguages) {
        var data = [];
        Ext.Array.each(availableLanguages, function(language) {
            data.push({
                languagecode: language.languagecode,
                name: language.name
            });
        }, this);
        return Ext.create('Ext.data.Store', {
            fields: ['languagecode', 'name'],
            data: data
        });
    },

    _loadLanguages: function() {
        devilry_i18n.LanguageSelectModel.load(null, {
            scope: this,
            success: this._onLoadLanguagesSuccess,
            failure: this._onLoadLanguagesFailure
        });
    },

    _onLoadLanguagesSuccess: function(languageRecord) {
        this.languageRecord = languageRecord;
        var store = this._createAvailableLanguagesStore(languageRecord.get('available'));
        this._addCombobox(store, languageRecord.get('selected'));
    },


    _onLoadLanguagesFailure: function(unused, operation) {
        // NOTE: We try multiple times, because quick page loads (like with
        //       instant redirects), has a tendency to make loading fail, which
        //       will show flash the error popup to the user.
        if(this.loadTries > 3) {
            this._showError(gettext('Failed to load languages. Try to reload the page.'));
        } else {
            this.loadTries ++;
            Ext.defer(this._loadLanguages, 1000, this);
        }
    },

    _showError: function(msg) {
        Ext.MessageBox.show({
            title: gettext('Error'),
            msg: msg,
            icon: Ext.MessageBox.ERROR
        });
    },

    _addCombobox: function(store, selected) {
        this.removeAll();
        this.add({
            xtype: 'combobox',
            queryMode: 'local',
            displayField: 'name',
            valueField: 'languagecode',
            forceSelection: true,
            editable: false,
            value: selected.languagecode,
            store: store,
            hideLabel: this.hideLabel,
            fieldLabel: this.fieldLabel,
            listeners: {
                scope: this,
                select: this._onSelect
            }
        });
    },

    _onSelect: function(combo, records) {
        var languagecode = records[0].get('languagecode');
        this.languageRecord.set('preferred', languagecode);
        Ext.getBody().mask(gettext('Saving') + '...');
        this.languageRecord.save({
            scope: this,
            success: this._onSaveSuccess,
            failure: this._onSaveFailure
        });
    },

    _onSaveFailure: function(unused, operation) {
        Ext.getBody().unmask();
        this._showError(gettext('Failed to save language choice.'));
    },

    _onSaveSuccess: function(languageRecord) {
        Ext.getBody().unmask();
        window.location.reload();
    }
});
