Ext.define('devilry.extjshelpers.HelpWindow', {
    extend: 'devilry.extjshelpers.AutoSizedWindow',
    alias: 'widget.helpwindow',
    modal: true,
    layout: 'fit',
    width: 1000,
    height: 800,
    closable: false, // To easy to double click and close an undelying window

    helptpl: Ext.create('Ext.XTemplate', '<div class="section helpsection">{helptext}</div>'),
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
