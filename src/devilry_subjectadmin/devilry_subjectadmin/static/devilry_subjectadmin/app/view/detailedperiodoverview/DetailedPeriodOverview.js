/**
 * Subject overview (overview of an subject).
 */
Ext.define('devilry_subjectadmin.view.detailedperiodoverview.DetailedPeriodOverview' ,{
    extend: 'Ext.container.Container',
    alias: 'widget.detailedperiodoverview',
    cls: 'devilry_detailedperiodoverview',
    requires: [
    ],


    /**
     * @cfg {String} [period_id] (required)
     */


    initComponent: function() {
        Ext.apply(this, {
            padding: '20',
            layout: 'border',
            items: [{
                //                cls: 'devilry_focuscontainer',
                xtype: 'box',
                cls: 'bootstrap',
                margin: '0 0 20 0',
                region: 'north',
                height: 20,
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
                xtype: '',
                region: 'center'
            }]
        });
        this.callParent(arguments);
    }
});
