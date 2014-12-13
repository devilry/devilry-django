Ext.define('devilry_i18n.LanguageSelectModel', {
    extend: 'Ext.data.Model',
    idProperty: 'preferred',
    fields: [
        {name: 'preferred',  type: 'string'},
        {name: 'selected',  type: 'auto'},
        {name: 'available',  type: 'auto'}
    ],

    proxy: {
        type: 'rest',
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_i18n/rest/languageselect',
        appendId: false,
        extraParams: {
            format: 'json'
        },
        reader: {
            type: 'json'
        }
    }
});
