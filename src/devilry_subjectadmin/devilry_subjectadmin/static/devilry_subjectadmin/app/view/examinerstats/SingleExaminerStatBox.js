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
        '<h4>{stats.examiner.user.displayname}</h4>',
        '<dl>',
            '<dt>', gettext('Corrected groups') ,'</dt>',
            '<dd>{stats.corrected_count}/{total_count}</dd>',

            '<dt>', gettext('Passed groups') ,'</dt>',
            '<dd class="text-success">{stats.passed_count}/{total_count}</dd>',

            '<dt>', gettext('Failed groups') ,'</dt>',
            '<dd class="text-warning">{stats.failed_count}/{total_count}</dd>',

            '<dt>', gettext('Groups waiting for feedback') ,'</dt>',
            '<dd>{stats.waitingforfeedback_count}/{total_count}</dd>',

            '<dt>', gettext('Groups waiting for deadline to expire') ,'</dt>',
            '<dd>{stats.waitingfordeliveries_count}/{total_count}</dd>',

            '<dt>', gettext('Points'), '</dt>',
            '<dd>',
                gettext('Average:'), ' {stats.points_avg} ',
                '<small class="muted">(',
                    gettext('Worst:'), '{stats.points_worst}, ',
                    gettext('Best:'), '{stats.points_best}',
                ')</small>',
            '</dd>',
        '</dl>'
    ],

    initComponent: function() {
        this._createChartStore();
        Ext.apply(this, {
            layout: 'column',
            items: [{
                xtype: 'box',
                columnWidth: 0.4,
                cls: 'bootstrap',
                tpl: this.bodytpl,
                data: {
                    stats: this.examinerstat.data,
                    total_count: this.examinerstat.get('groups').length
                }
            }, {
                xtype: 'chart',
                animate: true,
                store: this.chartStore,
                columnWidth: 0.6,
                height: 300,
                shadow: true,
                legend: {
                    position: 'right'
                },
                insetPadding: 30,
                theme: 'Base:gradients',
                series: [{
                    type: 'pie',
                    field: 'groups_percent',
                    showInLegend: true,
                    donut: false,
                    tips: {
                      trackMouse: true,
                      width: 140,
//                      height: ,
                      renderer: function(record, item) {
                        this.setTitle(record.get('title') + ': ' +
                            Math.round(record.get('groups_percent')) + '%');
                      }
                    },
                    highlight: {
                      segment: {
                        margin: 20
                      }
                    },
                    label: {
                        field: 'title',
                        display: 'rotate',
                        contrast: true,
                        font: '12px Ubuntu, sans-serif'
                    }
                }]
            }]
        });
        this.callParent(arguments);
    },

    _createChartStore:function () {
        var data = [{
            title: gettext('Passed groups'),
            groups_percent: this.examinerstat.get('passed_percent')
        }, {
            title: gettext('Failed groups'),
            groups_percent: this.examinerstat.get('failed_percent')
        }, {
            title: gettext('Waiting for feedback'),
            groups_percent: this.examinerstat.get('waitingforfeedback_percent')
        }, {
            title: gettext('Waiting for deadline to expire'),
            groups_percent: this.examinerstat.get('waitingfordeliveries_percent')
        }];
        this.chartStore = Ext.create('Ext.data.Store', {
            fields: [
                {name: 'title', type: 'string'},
                {name: 'groups_percent', type: 'float'}
            ],
            data: data,
            proxy: {
                type: 'memory'
            }
        });
    }
});