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
        'devilry_qualifiesforexam.view.preview.PreviewGrid'
    ],

    layout: 'border',

    initComponent: function() {
        Ext.apply(this, {
            items: [{
                xtype: 'previewgrid',
                region: 'center'
            }]
        });
        this.callParent(arguments);
    }
});
