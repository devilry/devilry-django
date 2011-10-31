Ext.define('devilry.student.models.StaticFeedback', {
    extend: 'devilry.extjshelpers.models.StaticFeedback',
    belongsTo: 'devilry.student.models.Delivery',
    proxy: Ext.create('devilry.extjshelpers.RestProxy', {
        url: '/student/restfulsimplifiedstaticfeedback/'
    })
});
