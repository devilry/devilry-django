Ext.define('devilry.i18n.EditRecordForm', {
    extend: 'Ext.form.Panel',
    alias: 'widget.i18n-editrecordform',
    
    /**
     * @cfg
     * 
     */
    record: undefined,

    initComponent: function() {
        var me = this;
        Ext.apply(this, {
            title: 'Translation',
            bodyPadding: 5,
            layout: 'fit',
            flex: 1,
            items: [{
                xtype: 'textarea',
                name: 'translation'
            }],
            buttons: [{
                text: 'Cancel',
                handler: function() {
                    var form = this.up('form').getForm();
                    var translation = form.getValues().translation;
                    if(translation === form.getRecord().get('translation')) {
                        this.up('window').close();
                    } else {
                        Ext.MessageBox.confirm('Close without saving?', 'This will loose any changes you have made to the translation.', function(btn) {
                            if(btn === 'yes') {
                                this.up('window').close();
                            }
                        }, this);
                    }
                }
            }, {
                text: 'Save',
                handler: function() {
                    var form = this.up('form').getForm();
                    form.updateRecord(form.getRecord());
                    this.up('window').close();
                }
            }]
        });
        this.callParent(arguments);
        this.loadRecord(this.record);
    }
});
