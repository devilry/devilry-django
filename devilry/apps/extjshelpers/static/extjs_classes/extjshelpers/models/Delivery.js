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
        {"type": "auto", "name": "alias_delivery"}
    ]
    //proxy: Ext.create('devilry.extjshelpers.RestProxy', {
        //url: '/administrator/restfulsimplifieddelivery/',
        //extraParams: {
            //getdata_in_qrystring: true,
            //result_fieldgroups: '["deadline", "assignment_group", "assignment"]'
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
