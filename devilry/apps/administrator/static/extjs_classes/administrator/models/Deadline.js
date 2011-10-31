Ext.define('devilry.administrator.models.Deadline', {
    extend: 'devilry.extjshelpers.models.Deadline',
    hasMany: {
        model: 'devilry.administrator.models.Delivery',
        name: 'deliveries',
        foreignKey: 'deadline'
    },
    proxy: Ext.create('devilry.extjshelpers.RestProxy', {
        url: '/administrator/restfulsimplifieddeadline/'
    })
});
