Ext.define('devilry.extjshelpers.ButtonBar', {
    extend: 'Ext.container.Container',
    cls: 'create-button-bar',
    bodyCls: 'create-button-bar-body',
    border: 0,
    height: 40,
    layout: {
        type: 'hbox',
        align: 'stretch',
        pack: 'center'
    },

    initComponent: function() {
        var me = this;
        this.callParent(arguments);

        Ext.each(this.buttons, function(button) {
            me.addButton(button.text, button.url, button.tooltip);
        });
    },

    addButton: function(text, url, tooltip) {
        if(this.items.items.size != 0) {
            this.add({
                xtype: 'component',
                width: 20
            });
        }
        var button = Ext.create('Ext.button.Button', {
            xtype: 'button',
            iconCls: 'icon-add-32',
            scale: 'large',
            text: text,
            handler: function() {
                window.location = url;
            },
            listeners: {
                render: function() {
                    console.log(tooltip);
                    Ext.create('Ext.tip.ToolTip', {
                        target: button.id,
                        anchor: 'top',
                        dismissDelay: 30000,
                        html: Ext.String.format('<div class="tooltip-title">{0}</div><p>{1}</p>',
                                                tooltip.title, tooltip.body)
                    });
                }
            }
        });
        this.add(button);
    }
});
