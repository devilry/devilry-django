Ext.define('devilry.gradeeditors.ConfigEditorWindow', {
    extend: 'Ext.window.Window',
    alias: 'widget.gradeconfigeditormainwin',
    title: 'Edit grade editor config',
    width: 500,
    height: 400,
    layout: 'fit',
    modal: true,

    config: {
        /**
         * @cfg
         * ID of an Assignment. (Required).
         */
        assignmentid: undefined,

        /**
         * @cfg
         * The data attribute of the record returned when loading the
         * grade-editor registry item. (Required).
         */
        registryitem: undefined
    },

    constructor: function(config) {
        this.callParent([config]);
        this.initConfig(config);
    },

    initComponent: function() {
        Ext.apply(this, {
            dockedItems: [{
                xtype: 'toolbar',
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
            }],

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
                    success: this.onLoadConfigEditorSuccess,
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
    onLoadConfigEditorSuccess: function() {
        this.getConfigEditor().getEl().mask('Loading current config');

        Ext.ModelManager.getModel(this.getConfigModelName()).load(this.assignmentid, {
            scope: this,
            callback: this.onLoadCurrentConfig
        });
    },

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
    onLoadCurrentConfig: function(record) {
        this.getConfigEditor().initializeEditor(record);
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
     */
    saveConfig: function(configstring, onFailure) {
        var me = this;

        var config = Ext.create(this.getConfigModelName(), {
            config: configstring,
            gradeeditorid: gradeeditorid,
            assignment: this.assignmentid
        });
        config.save(config, {
            scope: this.getConfigEditor(),
            success: function(response) {
                me.close();
            },
            failure: onFailure
        });
    },

    /**
     * Change the size of the window. Useful when the default size is
     * suboptimal for an editor.
     *
     * @param width New width.
     * @param height Ne height.
     * */
    changeSize: function(width, height) {
        this.setWidth(width);
        this.setHeight(height);
        this.center();
    }
});
