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

    /**
     * @cfg {Object} panelConfig
     * Config parameters for the panel.
     */

    initComponent: function() {
        var panelConfig = {xtype: 'chooseexaminerspanel'};
        Ext.apply(panelConfig, this.panelConfig);
        Ext.apply(this, {
            items: [panelConfig]
        });
        this.callParent(arguments);
    }
});
