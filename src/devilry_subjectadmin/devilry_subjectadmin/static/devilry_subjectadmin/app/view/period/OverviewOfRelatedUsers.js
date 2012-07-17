/**
 * Overview of relatated users on a period.
 */
Ext.define('devilry_subjectadmin.view.period.OverviewOfRelatedUsers', {
    extend: 'Ext.container.Container',
    alias: 'widget.overviewofrelatedusers',
    cls: 'devilry_subjectadmin_overviewofrelatedusers',
    requires: [
        'devilry_subjectadmin.view.period.ListOfRelatedUsers'
    ],

    initComponent: function() {
        Ext.apply(this, {
            autoScroll: true,
            layout: 'column',

            items: [{
                columnWidth: 0.4,
                xtype: 'box',
                tpl: '{msg}',
                data: {
                    msg: 'Help coming here'
                }
            }, {
                xtype: 'listofrelatedusers',
                columnWidth: .3,
                itemId: 'students',
                title: gettext('Students'),
                buttonText: gettext('Manage students'),
                css_suffix: 'students'
            }, {
                xtype: 'listofrelatedusers',
                columnWidth: .3,
                itemId: 'examiners',
                title: gettext('Examiners'),
                buttonText: gettext('Manage examiners'),
                css_suffix: 'examiners'
            }]
        });
        this.callParent(arguments);
    }
});
