// NOTE: This was ported from the old devilry.apps.student, so it does not follow the MVC architecture
Ext.define('devilry_student.view.browsehistory.BrowsePeriods', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.student-browseperiods',
    requires: [
        'devilry_student.view.browsehistory.PeriodGrid',
        'devilry_student.view.browsehistory.AssignmentGrid',
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
            border: 0,
            items: [{
                xtype: 'box',
                region: 'north',
                height: 'auto',
                cls: 'bootstrap',
                padding: '0 0 10 0',
                tpl: [
                    '<h1>{heading}</h1>',
                    '<p><small>', 
                        gettext('Browse all your {assignments_term} and {deliveries_term}, including assignments from old {periods_term}.'),
                    '</small></p>'
                ],
                data: {
                    heading: gettext('Browse'),
                    assignments_term: gettext('assignments'),
                    deliveries_term: gettext('deliveries'),
                    periods_term: gettext('periods')
                }
            }, {
                xtype: 'browsehistory_periodgrid',
                region: 'west',
                width: 340,
                split: true,
                listeners: {
                    scope: this,
                    select: this._onSelectPeriod
                }
            }, {
                xtype: 'browsehistory_assignmentgrid',
                region: 'center',
                urlCreateFn: this.urlCreateFn,
                urlCreateFnScope: this.urlCreateFnScope
            }]
        });
        this.callParent(arguments);
    },

    _onSelectPeriod: function(grid, periodRecord) {
        var assignmentGrid = this.down('browsehistory_assignmentgrid');
        assignmentGrid.loadGroupsInPeriod(periodRecord);
    }
});
