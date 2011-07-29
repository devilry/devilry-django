/** Restful API for gradeeditor RegistryItems */
Ext.define('devilry.gradeeditors.RestfulRegistryItem', {
    extend: 'Ext.data.Model',
    requires: ['devilry.extjshelpers.RestProxy'],

    fields: [
        {name: 'gradeeditorid', type: 'string'},
        {name: 'title', type: 'string'},
        {name: 'description', type: 'string'},
        {name: 'config_editor_url', type: 'string'},
        {name: 'draft_editor_url', type: 'string'}
    ],

    proxy: Ext.create('devilry.extjshelpers.RestProxy', {
        url: DevilrySettings.DEVILRY_MAIN_PAGE + '/gradeeditors/restfulgradeeditorconfig/',
        reader: {
            type: 'json',
            root: 'items',
            totalProperty: 'total'
        }
    })
});
