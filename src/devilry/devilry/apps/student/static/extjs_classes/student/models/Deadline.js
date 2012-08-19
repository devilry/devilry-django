Ext.define('devilry.student.models.Deadline', {
    extend: 'devilry.extjshelpers.models.Deadline',
    hasMany: {
        model: 'devilry.student.models.Delivery',
        name: 'deliveries',
        foreignKey: 'deadline'
    },
    proxy: Ext.create('devilry.extjshelpers.RestProxy', {
        url: '/student/restfulsimplifieddeadline/'
    })
});
