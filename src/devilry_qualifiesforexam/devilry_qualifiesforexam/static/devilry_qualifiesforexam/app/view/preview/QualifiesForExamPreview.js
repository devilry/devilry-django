Ext.define('devilry_qualifiesforexam.view.preview.QualifiesForExamPreview' ,{
    extend: 'Ext.container.Container',
    alias: 'widget.preview',
    cls: 'devilry_qualifiesforexam_preview',

    requires: [
    ],

    layout: 'border',

    initComponent: function() {
        Ext.apply(this, {
            items: [{
                xtype: 'box',
                region: 'center',
                html: 'todo'
            }]
        });
        this.callParent(arguments);
    }
});
