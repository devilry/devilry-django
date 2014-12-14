Ext.define('devilry_subjectadmin.view.examinerstats.ExaminerStatsOverview' ,{
    extend: 'Ext.container.Container',
    alias: 'widget.examinerstatsoverview',
    cls: 'devilry_subjectadmin_examinerstatsoverview',

    requires: [
        'devilry_subjectadmin.view.examinerstats.AveragePointsChart',
        'devilry_subjectadmin.view.examinerstats.AverageWordsChart',
        'devilry_subjectadmin.view.examinerstats.PassedGroupsChart'
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
            items: [{
                xtype: 'container',
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
                        '<h1 style="margin: 0;">', gettext('Statistics about examiners'), '</h1>',
                        '<p class="muted"><small>',
                            gettext('Summary in this section, in the next section.'),
                        '</small></p>'
                    ].join('')
                }, {
                    xtype: 'examinerstats_averagePointsChart',
                    height: 400
                }, {
                    xtype: 'examinerstats_averageWordsChart',
                    height: 400
                }, {
                    xtype: 'examinerstats_passedGroupsChart',
                    height: 400
                }]
            }, {
                xtype: 'container',
                margin: '40 0 0 0',
                layout: 'anchor',
                cls: 'devilry_focuscontainer',
                padding: 20,
//                style: 'background-color: #fff; border: 1px solid #ccc',
                defaults: {
                    anchor: '100%'
                },
                items: [{
                    xtype: 'box',
                    cls: 'bootstrap',
                    html: [
                        '<h2 style="margin: 0;">', gettext('Details'), '</h2>',
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
