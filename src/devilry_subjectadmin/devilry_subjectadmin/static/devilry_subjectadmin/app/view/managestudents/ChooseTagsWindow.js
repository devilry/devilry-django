Ext.define('devilry_subjectadmin.view.managestudents.ChooseTagsWindow', {
    extend: 'Ext.window.Window',
    alias: 'widget.choosetagswindow',
    cls: 'devilry_subjectadmin_choosetagswindow',

    layout: 'fit',
    closable: true,
    maximizable: true,
    modal: true,

    requires: [
        'devilry_subjectadmin.view.managestudents.ChooseTagsPanel'
    ],

    /**
     * @cfg {String} [buttonText]
     * Forwarded to ChooseTagsPanel.
     */

    initComponent: function() {
        Ext.apply(this, {
            items: {
                xtype: 'choosetagspanel',
                buttonText: this.buttonText
            }
        });
        this.callParent(arguments);
    }
});
