Ext.define('devilry.extjshelpers.models.Node', {
    extend: 'Ext.data.Model',
    requires: [
        'devilry.extjshelpers.proxies.Node'
    ],

    fields: [{
        "type": "int",
        "name": "id"
    }, {
        "type": "auto",
        "name": "parentnode"
    }, {
        "type": "auto",
        "name": "short_name"
    }, {
        "type": "auto",
        "name": "long_name"
    }],
    idProperty: 'id',

    proxy: Ext.create('devilry.extjshelpers.proxies.Node')
});
