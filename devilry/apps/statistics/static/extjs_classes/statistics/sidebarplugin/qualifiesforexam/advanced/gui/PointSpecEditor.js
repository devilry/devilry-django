Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.advanced.gui.PointSpecEditor', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.statistics-pointspeceditor',
    requires: [
        'devilry.statistics.sidebarplugin.qualifiesforexam.advanced.gui.ListOfAssignments',
        'devilry.statistics.sidebarplugin.qualifiesforexam.advanced.gui.RangeSelect',
        'devilry.statistics.sidebarplugin.qualifiesforexam.advanced.PointSpec'
    ],

    config: {
        assignment_store: undefined,
        pointspec: undefined
    },

    constructor: function(config) {
        this.callParent([config]);
        this.initConfig(config);
    },

    initComponent: function() {
        Ext.apply(this, {
            layout: {
                type: 'vbox',
                align: 'stretch'
            },
            items: [{
                xtype: 'statistics-rangeselect',
                height: 160,
                title: 'Require the following amount of points:',
                initialMin: this.pointspec? this.pointspec.min: undefined,
                initialMax: this.pointspec? this.pointspec.max: undefined
            }, {
                xtype: 'statistics-listofassignments',
                assignment_store: this.assignment_store,
                flex: 1,
                selected_assignments: this.pointspec? this.pointspec.assignments: undefined,
                title: '... in total on the following assignments:',
                rowPrefix: 'Highest score of: ',
                rowSplitter: ', '
            }]
        });
        this.callParent(arguments);
    },

    getResult: function() {
        var range = this.down('statistics-rangeselect').getForm().getFieldValues();
        var assignments = this.down('statistics-listofassignments').getArrayOfAssignmentIds();
        var pointSpec = Ext.create('devilry.statistics.sidebarplugin.qualifiesforexam.advanced.PointSpec', {
            assignments: assignments,
            min: range.min,
            max: range.max
        });
        return pointSpec;
    }
});
