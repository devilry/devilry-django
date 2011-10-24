Ext.define('devilry.examiner.models.StaticFeedback', {
    extend: 'devilry.extjshelpers.models.StaticFeedback',
    belongsTo: 'devilry.examiner.models.Delivery',
    proxy: Ext.create('devilry.extjshelpers.RestProxy', {
        url: '/examiner/restfulsimplifiedstaticfeedback/'
    })
});
