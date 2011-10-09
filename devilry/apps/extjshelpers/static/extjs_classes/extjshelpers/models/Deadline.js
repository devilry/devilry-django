Ext.define('devilry.extjshelpers.models.Deadline', {
    extend: 'Ext.data.Model',
    idProperty: 'id',
    fields: [
        {"type": "int", "name": "id"},
        {"type": "auto", "name": "text"},
        {"type": "date", "name": "deadline", "dateFormat": "Y-m-dTH:i:s"},
        {"type": "auto", "name": "assignment_group"},
        {"type": "auto", "name": "number_of_deliveries"},
        {"type": "bool", "name": "feedbacks_published"}
    ],
    hasMany: {
        model: 'devilry.extjshelpers.models.Delivery',
        name: 'deliveries',
        foreignKey: 'deadline'
    },

    proxy: Ext.create('devilry.extjshelpers.RestProxy', {
        url: Ext.String.format('/{0}/restfulsimplified{1}/', 'administrator', 'deadline')
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
        //url: Ext.String.format('/{0}/restfulsimplified{1}/', 'administrator', 'deadline')
    //}
});
