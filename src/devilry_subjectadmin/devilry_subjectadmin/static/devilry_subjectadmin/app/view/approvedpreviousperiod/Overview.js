Ext.define('devilry_subjectadmin.view.approvedpreviousperiod.Overview' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.approvedpreviousperiodoverview',
    cls: 'devilry_subjectadmin_approvedpreviousperiodoverview',
    requires: [
    ],

    /**
     * @cfg {String} period_id (required)
     */


    initComponent: function() {
        Ext.apply(this, {
            frame: false,
            border: 0,
            bodyPadding: 40,
            autoScroll: true,

            items: [{
                xtype: 'box',
                html: 'hello world'
            }]
        });
        this.callParent(arguments);
    }
});
