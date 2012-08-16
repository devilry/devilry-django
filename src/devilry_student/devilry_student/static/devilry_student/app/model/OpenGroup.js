Ext.define('devilry_student.model.OpenGroup', {
    extend: 'Ext.data.Model',

    idProperty: 'id',
    fields: [
        {name: 'id', type: 'int'},
        {name: 'name', type: 'string'},
        {name: 'assignment', type: 'auto'},
        {name: 'period', type: 'auto'},
        {name: 'subject', type: 'auto'},
        {name: 'active_deadline', type: 'auto'},
        {name: 'deliveries', type: 'int'}
    ]
});
