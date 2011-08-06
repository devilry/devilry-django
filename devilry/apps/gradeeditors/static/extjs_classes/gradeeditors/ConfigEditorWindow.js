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
        registryitem: undefined,


        /**
         * @cfg
         * A {@link devilry.extjshelpers.SingleRecordContainer} for the grade
         * editor config. (Required).
         */
        gradeeditorconfig_recordcontainer: undefined
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
    initializeEditor: function() {
        this.getConfigEditor().initializeEditor(this.gradeeditorconfig_recordcontainer.record.data);
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
        var me = this;
        var configrecord = Ext.create(this.getConfigModelName(), {
            config: configstring,
            gradeeditorid: this.gradeeditorconfig_recordcontainer.record.data.gradeeditorid,
            assignment: this.gradeeditorconfig_recordcontainer.record.data.assignment
        });
        configrecord.save({
            scope: this.getConfigEditor(),
            success: function(response) {
                me.gradeeditorconfig_recordcontainer.setRecord(configrecord);
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
