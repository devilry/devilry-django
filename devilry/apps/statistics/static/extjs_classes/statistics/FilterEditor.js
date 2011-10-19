Ext.define('devilry.statistics.FilterEditor', {
    extend: 'Ext.tab.Panel',
    alias: 'widget.statistics-filtereditor',
    requires: [
        'devilry.statistics.MustPassEditor',
        'devilry.statistics.PointSpecEditor'
    ],

    initComponent: function() {
        Ext.apply(this, {
            items: [{
                xtype: 'statistics-mustpasseditor',
                title: 'Must pass'
            }, {
                xtype: 'statistics-pointspeceditor',
                title: 'Must have points'
            }]
        });
        this.callParent(arguments);
    }
});
