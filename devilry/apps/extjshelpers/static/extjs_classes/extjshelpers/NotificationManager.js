Ext.define('devilry.extjshelpers.NotificationManager', {
    height: 0,
    requires: [
        'devilry.extjshelpers.Notification'
    ],
    singleton: true,

    create: function(config) {
        var n = Ext.widget('notification');
        n.setTitle(config.title);
        n.setMessage(config.message);
    }
});
