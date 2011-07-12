Ext.define('devilry.extjshelpers.ErrorList', {
    extend: 'Ext.panel.Panel',
    title: 'Errors',
    cls: 'errorlist',
    bodyCls: 'errorlist-body',
    hidden: true,
    margin: {
        bottom: 15
    },

    addError: function(error) {
        this.add({
            xtype: 'component',
            html: Ext.String.format('<p class="errorlist-item">{0}</p>', error)
        });
        this.show();
    },

    clearErrors: function() {
        this.removeAll();
        this.hide();
    }
});
