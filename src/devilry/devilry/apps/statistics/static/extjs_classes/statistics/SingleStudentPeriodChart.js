Ext.define('devilry.statistics.SingleStudentPeriodChart', {
    extend: 'Ext.chart.Chart',
    alias: 'widget.statistics-singlestudentperiodchart',
    cls: 'widget-statistics-singlestudentperiodchart',

    groupTpl: Ext.create('Ext.XTemplate',
        '<tpl for="candidates">',
        '   {.}<tpl if="xindex != xcount">, </tpl>',
        '</tpl>'
    ),

    hoverTpl: Ext.create('Ext.XTemplate',
        'Points: {feedback__points}'
    ),

    initComponent: function() {
        var me = this;
        Ext.apply(this, {
            style: 'background:#fff',
            animate: true,
            shadow: true,
            axes: [{
                type: 'Numeric',
                position: 'left',
                fields: ['feedback__points'],
                label: {
                    renderer: Ext.util.Format.numberRenderer('0,0')
                },
                title: 'Points',
                grid: true,
                minimum: 0
            }, {
                type: 'Category',
                position: 'bottom',
                fields: ['assignment__short_name'],
                title: 'Assignment',

                label: {
                    renderer: function(data) {
                        return me.groupTpl.apply({candidates: data});
                    }
                }
            }],
            series: [{
                type: 'column',
                axis: 'left',
                highlight: true,
                tips: {
                    trackMouse: true,
                    width: 140,
                    height: 28,
                    renderer: function(storeItem, item) {
                        this.setTitle(me.hoverTpl.apply(storeItem.data));
                    }
                },
                label: {
                    display: 'insideEnd',
                    'text-anchor': 'middle',
                    field: 'feedback__grade',
                    //orientation: 'vertical',
                    color: '#333'
                },
                xField: 'id',
                yField: 'feedback__points',

                renderer: function(sprite, record, attr, index, store) {
                    var color = record.get('feedback__is_passing_grade')? '#77B300': '#CC4400';
                    return Ext.apply(attr, {
                        fill: color
                    });
                }
            }]
        });
        this.callParent(arguments);
    }
});
