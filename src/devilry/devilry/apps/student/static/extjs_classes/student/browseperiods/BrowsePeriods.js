Ext.define('devilry.student.browseperiods.BrowsePeriods', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.student-browseperiods',
    requires: [
        'devilry.student.browseperiods.PeriodGrid',
        'devilry.student.browseperiods.AssignmentGrid',
        'devilry.statistics.OverviewOfSingleStudent'
    ],

    /**
     * @cfg {Function} [urlCreateFn]
     * Function to call to genereate urls. Takes an AssignmentGroup record as parameter.
     */

    /**
     * @cfg {Object} [urlCreateFnScope]
     * Scope of ``urlCreateFn``.
     */
    
    initComponent: function() {
        Ext.apply(this, {
            layout: 'border',
            items: [{
                xtype: 'student-browseperiods-periodgrid',
                region: 'west',
                width: 250,
                split: true,
                listeners: {
                    scope: this,
                    select: this._onSelectPeriod
                }
            }, {
                xtype: 'student-browseperiods-assignmentgrid',
                region: 'center',
                urlCreateFn: this.urlCreateFn,
                urlCreateFnScope: this.urlCreateFnScope
            }]
        });
        this.callParent(arguments);
    },

    _onSelectPeriod: function(grid, periodRecord) {
        var assignmentGrid = this.down('student-browseperiods-assignmentgrid');
        assignmentGrid.loadGroupsInPeriod(periodRecord);
    }
});
