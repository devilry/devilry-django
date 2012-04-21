Ext.define('devilry.examiner.models.Deadline', {
    extend: 'devilry.extjshelpers.models.Deadline',
    hasMany: {
        model: 'devilry.examiner.models.Delivery',
        name: 'deliveries',
        foreignKey: 'deadline'
    },
    proxy: Ext.create('devilry.extjshelpers.RestProxy', {
        url: '/examiner/restfulsimplifieddeadline/'
    })
});
