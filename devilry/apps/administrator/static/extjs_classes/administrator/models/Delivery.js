Ext.define('devilry.administrator.models.Delivery', {
    extend: 'devilry.extjshelpers.models.Delivery',
    belongsTo: 'devilry.administrator.models.Deadline',
    proxy: Ext.create('devilry.extjshelpers.RestProxy', {
        url: '/administrator/restfulsimplifieddelivery/'
    })
});
