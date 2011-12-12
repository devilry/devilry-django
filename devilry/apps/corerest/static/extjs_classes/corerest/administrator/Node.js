Ext.define('devilry.corerest.administrator.Node', {
    extend:'Ext.data.Model',
    idProperty:'id',
    fields:[
        {"type":"int", "name":"id"},
        {"type":"int", "name":"parentnode_id"},
        {"type":"string", "name":"short_name"},
        {"type":"string", "name":"long_name"}
    ],
    proxy: {
        type: 'rest',
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/corerest/administrator/node/',
        extraParams: {
            _devilry_accept: 'application/json'
        },
        reader: {
            type: 'json',
            root: 'items',
            record: 'item'
        }
    }
});