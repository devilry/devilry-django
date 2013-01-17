Ext.define('devilry_qualifiesforexam.view.preview.QualifiesForExamPreview' ,{
    extend: 'Ext.container.Container',
    alias: 'widget.preview',
    cls: 'devilry_qualifiesforexam_preview',

    /**
     * @cfg {string} [pluginsessionid]
     */

    /**
     * @cfg {string} [pluginid]
     */

    /**
     * @cfg {int} [periodid]
     */

    requires: [
        'devilry_qualifiesforexam.view.preview.PreviewGrid',
        'devilry_extjsextras.PrimaryButton'
    ],


    summaryTpl: [
        '<h1 style="margin: 0 0 10px 0;">',
            gettext('Preview and confirm'),
        '</h1>',
        '<p>',
            gettext('The table shows the result of your choices.'),
        '</p>'
    ],

    initComponent: function() {
        Ext.apply(this, {
            autoScroll: true,
            layout: 'anchor',
            padding: '40 40 0 40',
            items: [{
                xtype: 'container',
                cls: 'devilry_focuscontainer bootstrap',
                padding: 20,
                margin: '0 0 20 0',
                layout: 'fit',
                anchor: '100%',
                items: [{
                    xtype: 'panel',
                    itemId: 'summary',
                    tpl: this.summaryTpl,
                    border: false,
                    data: {},
                    dockedItems: {
                        xtype: 'toolbar',
                        dock: 'bottom',
                        ui: 'footer',
                        items: [{
                            xtype: 'button',
                            itemId: 'backButton',
                            scale: 'large',
                            text: gettext('Back')
                        }, {
                            xtype: 'primarybutton',
                            itemId: 'saveButton',
                            text: gettext('Save')
                        }]
                    }
                }]
            }, {
                xtype: 'previewgrid',
                anchor: '100%',
                height: 300, // Initial height before it is autoset
                autoHeightMargin: 100
            }, {
                xtype: 'box',
                height: 40 // NOTE: get a "margin" below the table - padding does not seem to be respected
            }]
        });
        this.callParent(arguments);
    }
});
