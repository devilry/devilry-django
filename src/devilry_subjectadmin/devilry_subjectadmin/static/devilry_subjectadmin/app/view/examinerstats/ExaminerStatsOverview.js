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

    autoScroll: true, // Autoscroll on overflow

    initComponent: function() {
        Ext.apply(this, {
            layout: 'anchor',
            defaults: {
                anchor: '100%'
            },
            items: []
        });
        this.callParent(arguments);
    }
});
