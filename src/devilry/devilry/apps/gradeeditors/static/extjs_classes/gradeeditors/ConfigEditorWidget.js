/** Config editor widget. */
Ext.define('devilry.gradeeditors.ConfigEditorWidget', {
    extend: 'Ext.container.Container',
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


    /**
     * @cfg {String} [helpCls]
     * The css class(es) for the help box.
     */
    helpCls: 'bootstrap',


    initComponent: function() {
        Ext.apply(this, {
            layout: 'fit',
            items: [{
                xtype: 'box',
                html: gettext('Loading') + ' ...'
            }]
        });
        this.callParent(arguments);

        this.gradeEditorPanel = Ext.widget('panel', {
            border: false,
            frame: false,
            loader: {
                url: this.registryitem.config_editor_url,
                renderer: 'component',
                autoLoad: true,
                loadMask: true,
                scope: this, // for success and failure
                success: this._initializeEditor,
                failure: this._onLoadConfigEditorFailure
            }
        });
    },

    /**
     * @private
     */
    _getConfigModelName: function() {
        return 'devilry.apps.gradeeditors.simplified.administrator.SimplifiedConfig';
    },

    /**
     * @private
     */
    _onLoadConfigEditorFailure: function(elementloader, response) {
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
    _initializeEditor: function() {
        this.removeAll();
        this.gradeEditorPanel.padding = 0;
        this.gradeEditorPanel.margin = '0 40 0 0';
        if(this._getConfigEditor().help) {
            var helphtml = this._getConfigEditor().help;
            this.gradeEditorPanel.columnWidth = 0.6;
            this.add({
                xtype: 'container',
                layout: 'column',
                items: [this.gradeEditorPanel, {
                    xtype: 'box',
                    cls: this.helpCls,
                    padding: 0,
                    html: helphtml,
                    columnWidth: 0.4
                }]
            });
        } else {
            this.add(this.gradeEditorPanel);
        }

        this._getConfigEditor().initializeEditor(this.gradeEditorConfigRecord.data);
    },


    /**
     * @private
     * Get the config editor.
     */
    _getConfigEditor: function() {
        return this.gradeEditorPanel.getComponent(0);
    },

    /**
     * Call the onSave() method in the config editor. Typically used by a save button event handler.
     */
    triggerSave: function() {
        this._getConfigEditor().onSave();
    },


    /**
     * Called to save a configstring.
     */
    saveConfig: function(configstring, onFailure) {
        onFailure = onFailure || devilry.gradeeditors.FailureHandler.onFailure;
        var me = this;
        var configrecord = Ext.create(this._getConfigModelName(), {
            config: configstring,
            gradeeditorid: this.gradeEditorConfigRecord.get('gradeeditorid'),
            assignment: this.gradeEditorConfigRecord.get('assignment')
        });
        configrecord.save({
            scope: this._getConfigEditor(),
            success: function(response) {
                me.fireEvent('saveSuccess', me, configrecord);
            },
            failure: onFailure
        });
    }
});
