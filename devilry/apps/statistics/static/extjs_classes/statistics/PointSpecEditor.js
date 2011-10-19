Ext.define('devilry.statistics.PointSpecEditor', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.statistics-pointspeceditor',
    requires: [
        'devilry.statistics.ListOfAssignments',
        'devilry.statistics.RangeSelect',
        'devilry.statistics.PointSpec'
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
            layout: {
                type: 'vbox',
                align: 'stretch'
            },
            items: [{
                xtype: 'statistics-rangeselect',
                height: 160,
                title: 'Require the following amount of points:'
            }, {
                xtype: 'statistics-listofassignments',
                assignment_store: this.assignment_store,
                flex: 1,
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
        var pointSpec = Ext.create('devilry.statistics.PointSpec', {
            assignments: assignments,
            min: range.min,
            max: range.max
        });
        return pointSpec;
    }
});
