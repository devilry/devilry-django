Ext.define('devilry.student.browseperiods.BrowsePeriods', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.student-browseperiods',
    requires: [
        'devilry.student.browseperiods.PeriodGrid',
        'devilry.student.browseperiods.AssignmentGrid'
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
                xtype: 'panel',
                region: 'center',
                layout: 'border',
                items: [{
                    xtype: 'student-browseperiods-assignmentgrid',
                    region: 'center',
                    listeners: {
                        scope: this,
                        select: this._onSelectAssignment
                    }
                }, {
                    xtype: 'panel',
                    region: 'south',
                    title: '',
                    collapsible: true,
                    height: 200,
                    html: 'Overview'
                }]
            }]
        });
        this.callParent(arguments);
    },

    _onSelectPeriod: function(grid, periodRecord) {
        var assignmentGrid = this.down('student-browseperiods-assignmentgrid');
        assignmentGrid.loadGroupsInPeriod(periodRecord);
    },

    _onSelectAssignment: function(grid, record) {
        console.log('hei');
    }
});
