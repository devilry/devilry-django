Ext.define('devilry.i18n.LoadTranslationPanel', {
    extend: 'Ext.form.Panel',
    alias: 'widget.i18n-loadtranslationpanel',
    
    help: 'Load one of the translations available the server, or paste the contents of an existing translation JSON export file into the text area.',

    /**
     * @cfg
     */
    index: undefined,
    
    initComponent: function() {
        this._createIndexStore();
        Ext.apply(this, {
            bodyPadding: 5,
            tbar: [{
                xtype: 'combobox',
                fieldLabel: 'Load from server',
                store: this.indexstore,
                queryMode: 'local',
                displayField: 'display',
                valueField: 'name',
                listeners: {
                    scope: this,
                    select: this._onSelectExisting
                }
            }],
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
    },

    _onSelectExisting: function(combo, records) {
        var record = records[0];
        var name = record.get('name');
        Ext.Ajax.request({
            url: Ext.String.format('{0}/i18n/{1}.json', DevilrySettings.DEVILRY_STATIC_URL, name),
            scope: this,
            success: function(response) {
                var data = response.responseText;
                this.down('textarea').setValue(data);
            }
        });
    },

    _createIndexStore: function() {
        this.indexstore = Ext.create('Ext.data.Store', {
            autoDestroy: true,
            fields: ['name', 'display']
        });
        Ext.each(this.index, function(name, index) {
            this.indexstore.add({name: name, display: name.replace('messages_', '').replace('messages', 'DEFAULT')});
        }, this);
    }
});
