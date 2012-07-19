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
                tpl: '<p>{general}</p><p>{tagging}</p>',
                cls: 'bootstrap',
                padding: '5 20 0 0',
                data: {
                    general: gettext('These users are available when creating/managing assignments.'),
                    tagging: gettext('Students and examiners can be tagged, and students can easily be assigned to an examiner on assignments as long as they have at least one tag in common.')
                }
            }, {
                xtype: 'listofrelatedusers',
                columnWidth: .3,
                itemId: 'students',
                title: gettext('Students'),
                buttonText: gettext('Manage students'),
                css_suffix: 'students',
                managepanelxtype: 'managerelatedstudentspanel'
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
