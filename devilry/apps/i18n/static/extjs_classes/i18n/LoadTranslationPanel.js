Ext.define('devilry.i18n.LoadTranslationPanel', {
    extend: 'Ext.form.Panel',
    alias: 'widget.i18n-loadtranslationpanel',
    
    help: 'Paste the contents of an existing translation JSON export file into the text area.',
    
    initComponent: function() {
        Ext.apply(this, {
            bodyPadding: 5,
            layout: {
                type: 'hbox',
                align: 'stretch'
            },
            items: [{
                xtype: 'textarea',
                name: 'exportdata',
                flex: 7
            }, {
                xtype: 'box',
                cls: 'helpsection',
                html: this.help,
                flex: 3
            }],

            buttons: [{
                text: 'Cancel',
                handler: function() {
                    this.up('window').close();
                }
            }, {
                text: 'Load',
                listeners: {
                    scope: this,
                    click: function() {
                        var form = this.getForm();
                        var exportdata = form.getValues().exportdata;
                        this.fireEvent('exportdataLoaded', exportdata);
                        this.up('window').close();
                    }
                }
            }]
        });
        this.callParent(arguments);
    }
});
