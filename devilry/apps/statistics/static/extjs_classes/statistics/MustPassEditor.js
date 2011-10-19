Ext.define('devilry.statistics.MustPassEditor', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.statistics-mustpasseditor',
    requires: [
        'devilry.statistics.ListOfAssignments'
    ],

    initComponent: function() {
        Ext.apply(this, {
            layout: 'fit',
            items: {
                xtype: 'statistics-listofassignments',
                title: 'Require passing grade on the following assignments:'
            }
        });
        this.callParent(arguments);
    }
});
