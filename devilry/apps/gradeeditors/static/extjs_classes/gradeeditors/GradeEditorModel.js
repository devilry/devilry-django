Ext.define('devilry.gradeeditors.GradeEditorModel', {
    extend: 'Ext.data.Model',
    requires: ['devilry.extjshelpers.RestProxy'],

    fields: [{
        name: 'gradeeditorid',
        type: 'string'
    }, {
        name: 'title',
        type: 'string'
    }, {
        name: 'description',
        type: 'string'
    }],

    idProperty: 'gradeeditorid',

    proxy: Ext.create('devilry.extjshelpers.RestProxy', {
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/gradeeditors/restfulgradeeditorconfig/',
        reader: {
            type: 'json',
            root: 'items',
            totalProperty: 'total'
        }
    })
});
