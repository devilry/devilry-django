Ext.define('devilry.extjshelpers.models.Delivery', {
    extend: 'Ext.data.Model',
    idProperty: 'id',
    fields: [
        {"type": "int", "name": "id"},
        {"type": "int", "name": "number"},
        {"type": "date", "name": "time_of_delivery", "dateFormat": "Y-m-dTH:i:s"},
        {"type": "auto", "name": "deadline"},
        {"type": "bool", "name": "successful"},
        {"type": "int", "name": "delivery_type"},
        {"type": "int", "name": "deadline"},
        {"type": "auto", "name": "alias_delivery"}
    ],

    belongsTo: 'devilry.extjshelpers.models.Deadline',

    proxy: Ext.create('devilry.extjshelpers.RestProxy', {
        url: Ext.String.format('/{0}/restfulsimplified{1}/', 'administrator', 'delivery')
    })

    //proxy: {
        //type: 'rest',
        //reader: {
            //type: 'json',
            //root: 'items',
            //totalProperty: 'total'
        //},
        //writer: {
            //type: 'json'
        //},
        //url: Ext.String.format('/{0}/restfulsimplified{1}/', 'administrator', 'delivery')
    //}
});
