Ext.define('devilry.student.browseperiods.BrowsePeriods', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.student-browseperiods',
    requires: [
        'devilry.student.browseperiods.PeriodGrid',
        'devilry.student.browseperiods.AssignmentGrid',
        'devilry.statistics.OverviewOfSingleStudent'
    ],
    
    initComponent: function() {
        Ext.apply(this, {
            layout: 'border',
            items: [{
                xtype: 'student-browseperiods-periodgrid',
                region: 'west',
                width: 200,
                listeners: {
                    scope: this,
                    select: this._onSelectPeriod
                }
            }, {
                xtype: 'student-browseperiods-assignmentgrid',
                region: 'center'
            }]
        });
        this.callParent(arguments);
    },

    _onSelectPeriod: function(grid, periodRecord) {
        var assignmentGrid = this.down('student-browseperiods-assignmentgrid');
        assignmentGrid.loadGroupsInPeriod(periodRecord);
    }
});
