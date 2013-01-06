Ext.define('devilry_qualifiesforexam.view.preview.QualifiesForExamPreview' ,{
    extend: 'Ext.container.Container',
    alias: 'widget.preview',
    cls: 'devilry_qualifiesforexam_preview',

    /**
     * @cfg {string} [pluginsessionid]
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
            gettext('Please click the save-button below when you are ready proceed. The table below shows the result of your choices.'),
        '</p>'
    ],

    initComponent: function() {
        Ext.apply(this, {
            layout: 'anchor',
            padding: '20',
            items: [{
                xtype: 'container',
                cls: 'devilry_focuscontainer bootstrap',
                padding: 20,
                height: 195,
                margin: '0 0 20 0',
                layout: 'fit',
                items: [{
                    xtype: 'panel',
                    itemId: 'summary',
                    tpl: this.summaryTpl,
                    autoScroll: true,
                    border: false,
                    data: {},
                    fbar: [{
                        xtype: 'button',
                        itemId: 'backButton',
                        text: gettext('Back')
                    }, {
                        xtype: 'primarybutton',
                        itemId: 'saveButton',
                        text: gettext('Save')
                    }]
                }]
            }, {
                xtype: 'previewgrid',
                anchor: '0 -215'
            }]
        });
        this.callParent(arguments);
    }
});
