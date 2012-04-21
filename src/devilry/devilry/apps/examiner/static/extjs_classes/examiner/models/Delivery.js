Ext.define('devilry.examiner.models.Delivery', {
    extend: 'devilry.extjshelpers.models.Delivery',
    belongsTo: 'devilry.examiner.models.Deadline',
    hasMany: {
        model: 'devilry.examiner.models.StaticFeedback',
        name: 'staticfeedbacks',
        foreignKey: 'delivery'
    },
    proxy: Ext.create('devilry.extjshelpers.RestProxy', {
        url: '/examiner/restfulsimplifieddelivery/'
    })
});
