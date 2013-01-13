Ext.define('devilry_subjectadmin.view.detailedperiodoverview.DetailedPeriodOverview' ,{
    extend: 'Ext.container.Container',
    alias: 'widget.detailedperiodoverview',
    cls: 'devilry_detailedperiodoverview',
    requires: [
        'devilry_subjectadmin.view.detailedperiodoverview.PeriodOverviewGrid'
    ],


    /**
     * @cfg {String} [period_id] (required)
     */


    initComponent: function() {
        Ext.apply(this, {
            padding: '20',
            layout: 'border',
            style: 'background-color: transparent !important;',
            items: [{
                //                cls: 'devilry_focuscontainer',
                xtype: 'box',
                cls: 'bootstrap',
                region: 'north',
                height: 24,
                itemId: 'header',
                tpl: [
                    '<h1 style="margin: 0; padding: 0; font-size: 14px; line-height: 14px;">',
                        '<tpl if="loading">',
                            gettext('Loading'), ' ...',
                        '<tpl else>',
                            gettext('Detailed overview of {periodpath}'),
                    '</tpl>',
                    '</h1>'
                ],
                data: {
                    loading: true
                }
            }, {
                xtype: 'detailedperiodoverviewgrid',
                region: 'center',
                period_id: this.period_id
            }]
        });
        this.callParent(arguments);
    }
});
