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
    //proxy: Ext.create('devilry.extjshelpers.RestProxy', {
        //url: '/administrator/restfulsimplifiednode/',
        //extraParams: {
            //getdata_in_qrystring: true
        //},
        //reader: {
            //type: 'json',
            //root: 'items',
            //totalProperty: 'total'
        //},
        //writer: {
            //type: 'json'
        //}
    //})
});
