Ext.define('devilry_subjectadmin.view.guidesystem.Pointer', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.guidesystem_pointer',
    requires: [
        'Ext.draw.Component'
    ],
    cls: 'devilry_subjectadmin_guidesystem_pointer',

    floating: true,

    width: 100,
    height: 100,
    border: false,

    initComponent: function() {
        Ext.apply(this, {
            bodyStyle: 'background-color: transparent !important;',
            //bodyStyle: 'background-color: red !important;',
            style: 'background-color: transparent !important;',
            frame: false,
            shadow: false,
            layout: 'fit',
            tpl: '<img src="{staticurl}/devilry_theme/resources/hugearrow/hugearrow_left.png" border="0"/>',
            data: {
                staticurl: DevilrySettings.DEVILRY_STATIC_URL
            }
        });
        this.callParent(arguments);
    }
});
