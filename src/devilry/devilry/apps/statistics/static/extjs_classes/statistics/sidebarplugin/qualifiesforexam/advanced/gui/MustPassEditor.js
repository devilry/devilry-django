Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.advanced.gui.MustPassEditor', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.statistics-mustpasseditor',
    requires: [
        'devilry.statistics.sidebarplugin.qualifiesforexam.advanced.gui.ListOfAssignments'
    ],

    config: {
        assignment_store: undefined,
        must_pass: undefined
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
                selected_assignments: this.must_pass,
                assignment_store: this.assignment_store
            }
        });
        this.callParent(arguments);
    },

    getResult: function() {
        return this.down('statistics-listofassignments').getArrayOfAssignmentIds();
    }
});
