Ext.define('devilry.administrator.models.Delivery', {
    extend: 'devilry.extjshelpers.models.Delivery',
    belongsTo: 'devilry.administrator.models.Deadline',
    hasMany: {
        model: 'devilry.administrator.models.StaticFeedback',
        name: 'staticfeedbacks',
        foreignKey: 'delivery'
    },
    proxy: Ext.create('devilry.extjshelpers.RestProxy', {
        url: '/administrator/restfulsimplifieddelivery/'
    })
});
