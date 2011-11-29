Ext.define('devilry.i18n.TranslateGuiModel', {
    extend: 'Ext.data.Model',
    idProperty: 'key',
    fields: [
        {name: 'key', type: 'string'},
        {name: 'default', type: 'string'},
        {name: 'translation', type: 'string'}
    ]
});
