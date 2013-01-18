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
            layout: 'column',
            autoScroll: true, // Autoscroll on overflow
            padding: 40,
            items: [{
                xtype: 'container',
                columnWidth: 0.6,
                padding: 10,
                layout: 'anchor',
                cls: 'devilry_focuscontainer',
                defaults: {
                    anchor: '100%'
                },
                items: [{
                    xtype: 'box',
                    cls: 'bootstrap',
                    html: [
                        '<h1 style="margin: 0;">', gettext('Overview of examiners'), '</h1>',
                        '<p class="muted"><small>',
                            gettext('Statistics about your examiners.'),
                        '</small></p>'
                    ].join('')
                }]
            }, {
                xtype: 'container',
                columnWidth: 0.4,
                margin: '0 0 0 40',
                layout: 'anchor',
                cls: 'devilry_focuscontainer',
                padding: 10,
//                style: 'background-color: #fff; border: 1px solid #ccc',
                defaults: {
                    anchor: '100%'
                },
                items: [{
                    xtype: 'box',
                    cls: 'bootstrap',
                    html: [
                        '<h3 style="margin: 0;">', gettext('Details'), '</h3>',
                        '<p class="muted"><small>',
                            gettext('Detailed statistics for each examiner.'),
                        '</small></p>'
                    ].join('')
                }, {
                    xtype: 'container',
                    itemId: 'examinerStatBoxes',
                    items: []
                }]
            }]
        });
        this.callParent(arguments);
    }
});
