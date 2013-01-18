Ext.define('devilry_subjectadmin.view.examinerstats.PassedGroupsChart' ,{
    extend: 'Ext.chart.Chart',
    alias: 'widget.examinerstats_passedGroupsChart',
    cls: 'devilry_subjectadmin_examinerstats_passedGroupsChart',

    animate: true,
    shadow: true,
    store: 'ExaminerStats',
    axes: [{
        type: 'Numeric',
        position: 'left',
        fields: ['passed_percent'],
        label: {
            renderer: Ext.util.Format.numberRenderer('0')
        },
        title: gettext('Passed groups (percent)'),
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
                return examiner.user.displayname;
            } 
        }
    }],

    series: [{
        type: 'column',
        axis: 'bottom',
        highlight: true,
        tips: {
            trackMouse: true,
            width: 220,
//            height: 28,
            renderer: function(record, item) {
                this.setTitle([
                    record.get('examiner').user.displayname,
                    ': ', record.get('passed_percent'), '% '
                ].join(''));
            }
        },
        label: {
            display: 'insideEnd',
            field: 'passed_percent',
            renderer: Ext.util.Format.numberRenderer('0'),
            orientation: 'horizontal',
            contrast: true,
            'text-anchor': 'middle'
        },
        xField: 'examiner',
        yField: ['passed_percent'],

        renderer: function(sprite, record, attr, index, store) {
            return Ext.apply(attr, {
                fill: '#468847',
                stroke: '#222222'
            });
        }
    }]
});
