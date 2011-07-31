Ext.define('devilry.extjshelpers.proxies.Node', {
    extend: 'devilry.extjshelpers.RestProxy',
    url: '/administrator/restfulsimplifiednode/',
    extraParams: {
        getdata_in_qrystring: true
    },
    reader: {
        type: 'json',
        root: 'items',
        totalProperty: 'total'
    },
    writer: {
        type: 'json'
    }
});
