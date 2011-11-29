Ext.define('devilry.i18n.LoadFileForm', {
    extend: 'Ext.form.Panel',
    alias: 'widget.i18n-loadfileform',
    
    initComponent: function() {
        //this.addEvents('success');
        Ext.apply(this, {
            items: [{
                xtype: 'hiddenfield',
                name: 'content_type',
                value: 'text/html'
            }, {
                xtype: 'hiddenfield',
                name: 'xmlescape_content',
                value: 'true'
            }, {
                xtype: 'filefield',
                emptyText: 'Select a file',
                name: 'content'
            }],
            buttons: [{
                text: 'Cancel',
                handler: function() {
                    this.up('window').close();
                }
            }, {
                text: 'Load',
                handler: function() {
                    var form = this.up('form').getForm();
                    if(form.isValid()) {
                        form.submit({
                            waitMsg: 'Loading file...',
                            //scope: this,
                            success: function(form, action) {
                                Ext.MessageBox.alert('hei');
                                //this.fireEvent('success', this, action.result);
                            }
                        });
                    }
                    //this.up('window').close();
                }
            }]
        });
        this.callParent(arguments);
    }
});
