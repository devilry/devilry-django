Ext.define('devilry_subjectadmin.view.examinerstats.AveragePointsChart' ,{
    extend: 'Ext.chart.Chart',
    alias: 'widget.examinerstats_averagePointsChart',
    cls: 'devilry_subjectadmin_examinerstats_averagePointsChart',

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
        fields: ['points_avg'],
        label: {
            renderer: Ext.util.Format.numberRenderer('0.00')
        },
        title: gettext('Average points'),
        grid: true,
        minimum: 0
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
        highlight: true,
        tips: {
            trackMouse: true,
            width: 220,
//            height: 28,
            renderer: function(record, item) {
                this.setTitle([
                    record.get('examiner').user.displayname,
                    ': ', record.get('points_avg'), ' ',
                    gettext('points')
                ].join(''));
            }
        },
        label: {
            display: 'insideEnd',
            field: 'points_avg',
            renderer: Ext.util.Format.numberRenderer('0'),
            orientation: 'horizontal',
            contrast: true,
            'text-anchor': 'middle'
        },
        xField: 'examiner',
        yField: ['points_avg'],

        renderer: function(sprite, record, attr, index, store) {
            return Ext.apply(attr, {
                fill: '#0077b3',
                stroke: '#222222'
            });
        }
    }]
});
