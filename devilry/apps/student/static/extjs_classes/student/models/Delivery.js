Ext.define('devilry.student.models.Delivery', {
    extend: 'devilry.extjshelpers.models.Delivery',
    belongsTo: 'devilry.student.models.Deadline',
    hasMany: {
        model: 'devilry.student.models.StaticFeedback',
        name: 'staticfeedbacks',
        foreignKey: 'delivery'
    },
    proxy: Ext.create('devilry.extjshelpers.RestProxy', {
        url: '/student/restfulsimplifieddelivery/'
    })
});
