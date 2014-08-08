Ext.define('devilry_subjectadmin.view.examinerstats.PassedGroupsChart' ,{
    extend: 'Ext.chart.Chart',
    alias: 'widget.examinerstats_passedGroupsChart',
    cls: 'devilry_subjectadmin_examinerstats_passedGroupsChart',

    requires: [
        'Ext.chart.series.Column',
        'Ext.chart.axis.Numeric',
        'Ext.chart.axis.Category'
    ],

    animate: true,
    shadow: true,
    store: 'ExaminerStats',
    axes: [{
        type: 'Numeric',
        position: 'left',
        fields: ['passed_percent'],
        label: {
            renderer:function (value) {
                return Ext.String.format('{0}%', Ext.util.Format.number(value, '0.0'));
            }
        },
        title: gettext('Results/Progress'),
        grid: true,
        minimum: 0,
        maximum: 100
    }, {
        type: 'Category',
        position: 'bottom',
        fields: ['examiner'],
        title: gettext('Examiner'),
        label: {
            renderer:function (examiner) {
                if(typeof examiner != 'undefined') {
                    return examiner.user.displayname;
                }
            } 
        }
    }],

    series: [{
        type: 'column',
        axis: 'bottom',
        stacked: true,
        highlight: true,
        tips: {
            trackMouse: true,
            width: 220,
//            height: 28,
            renderer: function(record, item) {
                var labelMap = {
                    passed_percent: gettext('Passed groups'),
                    failed_percent: gettext('Failed groups'),
                    waitingforfeedback_percent: gettext('Waiting for feedback'),
                    waitingfordeliveries_percent: gettext('Waiting for deadline to expire'),
                    closedwithoutfeedback_percent: gettext('Closed without feedback')
                };
                var percent = Ext.util.Format.number(record.get(item.yField), '0.0');
                this.setTitle([
                    labelMap[item.yField], ': ',
                    percent, '% ',
                    ' (', record.get('examiner').user.displayname, ')'
                ].join(''));
            }
        },
        xField: 'examiner',
        yField: ['passed_percent', 'failed_percent', 'waitingforfeedback_percent', 'waitingfordeliveries_percent', 'closedwithoutfeedback_percent'],

        renderer: function(sprite, record, attr, index, store) {
            var yindex = index%5;
            var colorSet = [
                '#468847', // passed
                '#b94a48', // failed
                '#999999', // waitingforfeedback
                '#eeeeee', // waitingfordeliveries
                '#ff0000'  // closedwithoutfeedback
            ];
            var color = colorSet[yindex];
            return Ext.apply(attr, {
                fill: color,
                stroke: '#222222'
            });
        }
    }]
});
