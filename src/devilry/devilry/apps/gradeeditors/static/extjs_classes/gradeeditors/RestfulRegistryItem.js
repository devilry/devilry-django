/** Restful API for gradeeditor RegistryItems */
Ext.define('devilry.gradeeditors.RestfulRegistryItem', {
    extend: 'Ext.data.Model',

    fields: [
        {name: 'gradeeditorid', type: 'string'},
        {name: 'title', type: 'string'},
        {name: 'description', type: 'string'},
        {name: 'config_editor_url', type: 'string'},
        {name: 'draft_editor_url', type: 'string'}
    ],

    proxy: {
        type: 'devilryrestproxy',
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/gradeeditors/restfulgradeeditorconfig/',
        headers: {
            'X_DEVILRY_USE_EXTJS': true
        },
        reader: {
            type: 'json',
            root: 'items',
            totalProperty: 'total'
        }
    }
});
