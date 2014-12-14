Ext.define('devilry_subjectadmin.view.examinerstats.AverageWordsChart' ,{
    extend: 'Ext.chart.Chart',
    alias: 'widget.examinerstats_averageWordsChart',
    cls: 'devilry_subjectadmin_examinerstats_averageWordsChart',

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
        fields: ['feedback_words_avg'],
        label: {
            renderer: Ext.util.Format.numberRenderer('0.0')
        },
        title: gettext('Number words in feedback'),
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
                    ': ', record.get('feedback_words_avg'), ' ',
                    gettext('words')
                ].join(''));
            }
        },
        label: {
            display: 'insideEnd',
            field: 'feedback_words_avg',
            renderer: Ext.util.Format.numberRenderer('0'),
            orientation: 'horizontal',
            contrast: true,
            'text-anchor': 'middle'
        },
        xField: 'examiner',
        yField: ['feedback_words_avg'],

        renderer: function(sprite, record, attr, index, store) {
            return Ext.apply(attr, {
                fill: '#555555',
                stroke: '#222222'
            });
        }
    }]
});
