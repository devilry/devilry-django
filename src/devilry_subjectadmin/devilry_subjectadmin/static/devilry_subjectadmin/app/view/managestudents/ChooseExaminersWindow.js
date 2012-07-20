Ext.define('devilry_subjectadmin.view.managestudents.ChooseExaminersWindow', {
    extend: 'Ext.window.Window',
    alias: 'widget.chooseexaminerswindow',
    cls: 'devilry_subjectadmin_chooseexaminerswindow',

    requires: [
        'devilry_subjectadmin.view.managestudents.ChooseExaminersPanel'
    ],

    layout: 'fit',
    closable: true,
    width: 700,
    height: 500,
    maximizable: true,
    modal: true,

    initComponent: function() {
        Ext.apply(this, {
            items: {
                xtype: 'chooseexaminerspanel',
                sourceStore: this.sourceStore
            }
        });
        this.callParent(arguments);
    }
});
