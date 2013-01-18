Ext.define('devilry_subjectadmin.view.examinerstats.SingleExaminerStatBox' ,{
    extend: 'Ext.container.Container',
    alias: 'widget.singleexaminerstatobx',
    cls: 'devilry_subjectadmin_singleexaminerstatobx',

    requires: [
    ],

    /**
     * @cfg {devilry_subjectadmin.model.ExaminerStat} [examinerstat]
     */

    bodytpl: [
        '<h3>{stats.examiner.user.displayname}</h3>',
        '<dl>',
            '<dt>', gettext('Corrected groups') ,'</dt>',
            '<dd>{corrected_count}/{total_count}</dd>',

            '<dt>', gettext('Passed groups') ,'</dt>',
            '<dd class="text-success">{stats.passed.length}/{total_count}</dd>',

            '<dt>', gettext('Failed groups') ,'</dt>',
            '<dd class="text-warning">{stats.failed.length}/{total_count}</dd>',

            '<dt>', gettext('Groups waiting for feedback') ,'</dt>',
            '<dd>{stats.waitingforfeedback.length}/{total_count}</dd>',

            '<dt>', gettext('Groups waiting for deadline to expire') ,'</dt>',
            '<dd>{stats.waitingfordeliveries.length}/{total_count}</dd>',
        '</dl>'
    ],

    initComponent: function() {
        Ext.apply(this, {
            layout: 'anchor',
            defaults: {
                anchor: '100%'
            },
            items: [{
                xtype: 'box',
                cls: 'bootstrap',
                tpl: this.bodytpl,
                data: {
                    stats: this.examinerstat.data,
                    corrected_count: this.examinerstat.get('failed').length +
                        this.examinerstat.get('passed').length,
                    total_count: this.examinerstat.get('failed').length +
                        this.examinerstat.get('passed').length +
                        this.examinerstat.get('closedwithoutfeedback').length +
                        this.examinerstat.get('nodeadlines').length +
                        this.examinerstat.get('waitingforfeedback').length +
                        this.examinerstat.get('waitingfordeliveries').length
                }
            }]
        });
        this.callParent(arguments);
    }
});