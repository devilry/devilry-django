Ext.define('devilry.statistics.MustPassEditor', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.statistics-mustpasseditor',
    requires: [
        'devilry.statistics.ListOfAssignments'
    ],

    config: {
        assignment_store: undefined
    },

    constructor: function(config) {
        this.callParent([config]);
        this.initConfig(config);
    },

    initComponent: function() {
        Ext.apply(this, {
            layout: 'fit',
            items: {
                xtype: 'statistics-listofassignments',
                title: 'Require passing grade on the following assignments:',
                assignment_store: this.assignment_store
            }
        });
        this.callParent(arguments);
    },

    getResult: function() {
        return this.down('statistics-listofassignments').getArrayOfAssignmentIds();
    }
});
