Ext.define('devilry.extjshelpers.NotificationManager', {
    height: 0,
    requires: [
        'devilry.extjshelpers.Notification'
    ],
    singleton: true,

    show: function(config) {
        var n = Ext.widget('notification', {
            iconCls: config.iconCls
        });
        n.setTitle(config.title);
        n.setMessage(config.message);
        n.show();
    }
});
