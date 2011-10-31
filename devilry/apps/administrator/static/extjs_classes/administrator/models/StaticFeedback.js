Ext.define('devilry.administrator.models.StaticFeedback', {
    extend: 'devilry.extjshelpers.models.StaticFeedback',
    belongsTo: 'devilry.administrator.models.Delivery',
    proxy: Ext.create('devilry.extjshelpers.RestProxy', {
        url: '/administrator/restfulsimplifiedstaticfeedback/'
    })
});
