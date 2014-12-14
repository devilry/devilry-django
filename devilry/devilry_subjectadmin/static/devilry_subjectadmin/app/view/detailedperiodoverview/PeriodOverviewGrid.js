Ext.define('devilry_subjectadmin.view.detailedperiodoverview.PeriodOverviewGrid', {
    extend: 'devilry_subjectadmin.view.detailedperiodoverview.PeriodOverviewGridBase',
    alias: 'widget.detailedperiodoverviewgrid',
    cls: 'devilry_subjectadmin_detailedperiodoverviewgrid bootstrap',

    store: 'AggregatedRelatedStudentInfos',

    requires: [
        'devilry_subjectadmin.view.detailedperiodoverview.ExportPeriodOverviewMenu'
    ],

    /**
     * @cfg {int} [period_id]
     */

    setupToolbar: function() {
        this.callParent(arguments);
        Ext.Array.insert(this.tbar, 1, [{
            xtype: 'button',
            text: gettext('Export'),
            menu: {
                xtype: 'exportperiodoverviewmenu',
                period_id: this.period_id
            }
        }]);
    }
});
