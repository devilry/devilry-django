Ext.define('devilry.extjshelpers.HelpWindow', {
    extend: 'Ext.window.Window',
    alias: 'widget.helpwindow',
    modal: true,
    layout: 'fit',
    closable: false, // To easy to double click and close an undelying window

    helptpl: Ext.create('Ext.XTemplate', '<section class="helpsection">{helptext}</section>'),

    initComponent: function() {
        Ext.apply(this, {
            items: {
                xtype: 'box',
                cls: 'helpbox',
                autoScroll: true,
                html: this.helptpl.apply({helptext:this.helptext})
            },
            dockedItems: [{
                xtype: 'toolbar',
                ui: 'footer',
                dock: 'bottom',
                items: ['->', {
                    xtype: 'button',
                    text: 'Close help',
                    scale: 'large',
                    listeners: {
                        scope: this,
                        click: function() {
                            this.close();
                        }
                    }
                }, '->']
            }],
        });
        this.callParent(arguments);
    }
});
