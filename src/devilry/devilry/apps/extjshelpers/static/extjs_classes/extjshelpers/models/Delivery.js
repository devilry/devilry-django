Ext.define('devilry.extjshelpers.models.Delivery', {
    extend: 'Ext.data.Model',
    idProperty: 'id',
    fields: [
        {"type": "int", "name": "id"},
        {"type": "int", "name": "number"},
        {"type": "date", "name": "time_of_delivery", "dateFormat": "Y-m-d\\TH:i:s"},
        {"type": "auto", "name": "deadline"},
        {"type": "bool", "name": "successful"},
        {"type": "int", "name": "delivery_type"},
        {"type": "int", "name": "deadline"},
        {"type": "auto", "name": "alias_delivery"}
    ]
});
