Ext.define('devilry.extjshelpers.HelpWindow', {
    extend: 'Ext.window.Window',
    alias: 'widget.helpwindow',
    modal: true,
    layout: 'fit',
    width: 800,
    height: 600,
    closable: false, // To easy to double click and close an undelying window

    helptpl: Ext.create('Ext.XTemplate', '<div class="section helpsection">{helptext}</section>'),
    helpdata: {},

    initComponent: function() {
        Ext.apply(this, {
            items: {
                xtype: 'box',
                cls: 'helpbox',
                autoScroll: true,
                html: this.helptpl.apply(Ext.apply(this.helpdata, {helptext:this.helptext}))
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
            }]
        });
        this.callParent(arguments);
    }
});
