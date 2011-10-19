Ext.define('devilry.statistics.FilterEditor', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.statistics-filtereditor',
    requires: [
        'devilry.statistics.ListOfAssignments'
    ],

    initComponent: function() {
        Ext.apply(this, {
            items: [{
                xtype: 'statistics-listofassignments',
                title: 'Require passing grade on these assignments'
            }, {
                
            }]
        });
        this.callParent(arguments);
    }
});
