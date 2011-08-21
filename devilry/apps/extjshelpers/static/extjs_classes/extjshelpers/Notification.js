Ext.define('devilry.extjshelpers.Notification', {
    extend: 'Ext.window.Window',
    alias: 'widget.notification',

    initComponent: function() {
        Ext.apply(this, {
            iconCls: this.iconCls,
            cls: 'x-notification',
            width: 200,
            autoHeight: true,
            plain: true,
            border: false,
            draggable: false,
            shadow: true,
            //bodyStyle: 'text-align:center'
        });
        if (this.autoDestroy) {
            this.task = new Ext.util.DelayedTask(this.hide, this);
        } else {
            this.closable = true;
        }

        this.callParent(arguments);
    },


    setMessage: function(msg) {
        this.update(msg);
    },

    setTitle: function(title, iconCls) {
        devilry.extjshelpers.Notification.superclass.setTitle.call(this, title, iconCls || this.iconCls);
    },

    onDestroy: function() {
        devilry.extjshelpers.Notification.superclass.onDestroy.call(this);
    },

    cancelHiding: function() {
        this.addClass('fixed');
        if (this.autoDestroy) {
            this.task.cancel();
        }
    },

    afterShow: function() {
        devilry.extjshelpers.Notification.superclass.afterShow.call(this);
        Ext.fly(this.body.dom).on('click', this.cancelHiding, this);
        if (this.autoDestroy) {
            this.task.delay(this.hideDelay || 5000);
        }
    },

    beforeShow: function() {
        this.el.hide();
    },

    onShow: function() {
        var me = this;

        var pos = devilry.extjshelpers.NotificationManager.height + 10;
        this.el.alignTo(document, "tr-tr", [-20, 10 + pos]);
        devilry.extjshelpers.NotificationManager.height = pos + this.getHeight();

        this.el.slideIn('t', {
            duration: 500,
            listeners: {
                afteranimate: {
                    fn: function() {
                        me.el.show();
                    }
                }
            }
        });
    },

    onHide: function() {
        this.el.disableShadow();
        this.el.ghost("t", {
            duration: 500,
            remove: true
        });
        devilry.extjshelpers.NotificationManager.height -= this.getHeight() - 10;
    },

    focus: Ext.emptyFn
});
