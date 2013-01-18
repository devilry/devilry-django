Ext.define('devilry_subjectadmin.view.examinerstats.ExaminerStatsOverview' ,{
    extend: 'Ext.container.Container',
    alias: 'widget.examinerstatsoverview',
    cls: 'devilry_subjectadmin_examinerstatsoverview',

    requires: [
    ],

    /**
     * @cfg {int} [assignment_id]
     * The ID of the assignment to load examiner stats for.
     */


    initComponent: function() {
        Ext.apply(this, {
            layout: 'anchor',
            autoScroll: true, // Autoscroll on overflow
            padding: 40,
            defaults: {
                anchor: '100%'
            },
            items: [{
                xtype: 'container',
                itemId: 'examinerStatBoxes',
                cls: 'devilry_focuscontainer',
                padding: 10,
                items: []
            }]
        });
        this.callParent(arguments);
    }
});
