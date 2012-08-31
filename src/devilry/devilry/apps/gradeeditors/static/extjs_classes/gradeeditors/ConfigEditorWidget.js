/** Config editor widget. */
Ext.define('devilry.gradeeditors.ConfigEditorWidget', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.gradeconfigeditor',
    layout: 'fit',
    requires: [
        'devilry.gradeeditors.FailureHandler',
        'devilry.extjshelpers.HelpWindow'
    ],

    /**
     * @cfg {Object} [registryitem]
     * The data attribute of the record returned when loading the
     * grade-editor registry item. (Required).
     */


    /**
     * @cfg {Object} [gradeEditorConfigRecord]
     * The grade editor config record (Required).
     */


    initComponent: function() {
        this.buttonBar = Ext.widget('toolbar', {
            dock: 'bottom',
            ui: 'footer',
            items: ['->', {
                xtype: 'button',
                text: 'Save',
                scale: 'large',
                iconCls: 'icon-save-32',
                listeners: {
                    scope: this,
                    click: this.onSave
                }
            }]
        });

        Ext.apply(this, {
            dockedItems: [this.buttonBar],

            items: {
                xtype: 'panel',
                frame: false,
                border: false,
                layout: 'fit',
                loader: {
                    url: this.registryitem.config_editor_url,
                    renderer: 'component',
                    autoLoad: true,
                    loadMask: true,
                    scope: this, // for success and failure
                    success: this.initializeEditor,
                    failure: this.onLoadConfigEditorFailure
                }
            }
        });

        this.callParent(arguments);
    },

    /**
     * @private
     */
    getConfigModelName: function() {
        return 'devilry.apps.gradeeditors.simplified.administrator.SimplifiedConfig';
    },

    /**
     * @private
     */
    onLoadConfigEditorFailure: function(elementloader, response) {
        console.error(Ext.String.format(
            'Loading grade config editor failed with {0}: {1}',
            response.status, response.statusText
        ));
        if(response.status === 404) {
            console.error('Status code 404 indicates that the config_editor_url is invalid.');
        } else if(response.status === 200) {
            console.error('Status code 200 indicates that the config_editor_url contains javascript with syntax errors.');
        }
        console.error('Complete response object:');
        console.error(response);
    },

    /**
     * @private
     */
    onHelp: function() {
        this.helpwindow.show();
    },

    /**
     * @private
     */
    initializeEditor: function() {
        if(this.getConfigEditor().help) {
            this.helpwindow = Ext.widget('helpwindow', {
                title: 'Help',
                closeAction: 'hide',
                helptext: this.getConfigEditor().help
            });

            this.buttonBar.insert(0, {
                text: 'Help',
                iconCls: 'icon-help-32',
                scale: 'large',
                listeners: {
                    scope: this,
                    click: this.onHelp
                }
            });
        }

        this.getConfigEditor().initializeEditor(this.gradeEditorConfigRecord.data);
    },


    /**
     * @private
     * Get the config editor.
     */
    getConfigEditor: function() {
        return this.getComponent(0).getComponent(0);
    },

    /**
     * @private
     * Call the onSave() method in the config editor.
     */
    onSave: function() {
        this.getConfigEditor().onSave();
    },


    /**
     * Called to save a configstring.
     */
    saveConfig: function(configstring, onFailure) {
        onFailure = onFailure || devilry.gradeeditors.FailureHandler.onFailure;
        var me = this;
        var configrecord = Ext.create(this.getConfigModelName(), {
            config: configstring,
            gradeeditorid: this.gradeEditorConfigRecord.get('gradeeditorid'),
            assignment: this.gradeEditorConfigRecord.get('assignment')
        });
        configrecord.save({
            scope: this.getConfigEditor(),
            success: function(response) {
                me.fireEvent('saveSuccess', me, configrecord);
            },
            failure: onFailure
        });
    }
});
