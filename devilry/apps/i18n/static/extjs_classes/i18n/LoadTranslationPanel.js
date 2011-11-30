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
                title: 'Default value',
                flex: 7
            }, {
                xtype: 'box',
                cls: 'helpsection',
                html: this.help,
                flex: 3
            }]
        });
        this.callParent(arguments);
    }
});
