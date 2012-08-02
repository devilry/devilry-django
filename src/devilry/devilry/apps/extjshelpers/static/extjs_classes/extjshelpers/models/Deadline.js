Ext.define('devilry.extjshelpers.models.Deadline', {
    extend: 'Ext.data.Model',
    idProperty: 'id',
    fields: [
        {"type": "int", "name": "id"},
        {"type": "auto", "name": "text"},
        {"type": "date", "name": "deadline", "dateFormat": "Y-m-d\\TH:i:s"},
        {"type": "auto", "name": "assignment_group"},
        {"type": "auto", "name": "number_of_deliveries"},
        {"type": "bool", "name": "feedbacks_published"}
    ]
});
