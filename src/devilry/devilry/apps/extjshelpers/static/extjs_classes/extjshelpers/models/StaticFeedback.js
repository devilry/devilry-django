Ext.define('devilry.extjshelpers.models.StaticFeedback', {
    extend: 'Ext.data.Model',
    idProperty: 'id',
    fields: [
        {"type": "int", "name": "id"},
        {"type": "auto", "name": "grade"},
        {"type": "bool", "name": "is_passing_grade"},
        {"type": "auto", "name": "saved_by"},
        {"type": "date", "name": "save_timestamp", "dateFormat": "Y-m-d\\TH:i:s"},
        {"type": "int", "name": "delivery"},
        {"type": "auto", "name": "rendered_view"}
    ],
});
